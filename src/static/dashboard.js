document.addEventListener('alpine:init', () => {
    Alpine.data('dashboard', () => ({
        environments: {
            dev: { status: 'checking...', version: '--' },
            staging: { status: 'checking...', version: '--' },
            prod: { status: 'checking...', version: '--' }
        },
        liveTraffic: 0,
        init() {
            this.fetchStatus();
            this.fetchDeployments();
            this.fetchTraffic();
            
            setInterval(() => {
                this.fetchStatus();
                this.fetchDeployments();
                this.fetchTraffic();
            }, 2000);
        },

        getPort(env) {
            const ports = { dev: '8000', staging: '8081', prod: '8082' };
            return ports[env];
        },

        getStatusColor(status, isPing) {
            if (status === 'healthy') return isPing ? 'bg-green-400' : 'bg-green-500';
            if (status === 'restarting' || status === 'deploying') return isPing ? 'bg-yellow-400' : 'bg-yellow-500';
            return isPing ? 'bg-red-400' : 'bg-red-500';
        },

        getTextColor(status) {
            if (status === 'healthy') return 'text-green-400';
            if (status === 'restarting' || status === 'deploying') return 'text-yellow-400';
            return 'text-red-400';
        },

        async fetchStatus() {
            try {
                let currentlyRestarting = [];
                for (let env in this.environments) {
                    if (this.environments[env].status === 'restarting' || this.environments[env].status === 'deploying') {
                        currentlyRestarting.push(env);
                    }
                }

                const res = await fetch('/api/environments');
                const data = await res.json();
                
                for (let env in data) {
                    if (!currentlyRestarting.includes(env)) {
                        this.environments[env] = data[env];
                    }
                }
            } catch (err) {
                console.error("Backend unreachable or restarting:", err);
            }
        },

        async fetchDeployments() {
            try {
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                const res = await fetch(`/api/deployments?tz=${tz}`);
                this.deployments = await res.json();
            } catch (err) {
                console.error("Failed to fetch deployments:", err);
            }
        },

        async fetchTraffic() {
            try {
                const res = await fetch('/api/traffic');
                const data = await res.json();
                this.liveTraffic = data.requests || 0;
            } catch (err) {
                console.warn("Traffic api error:", err);
            }
        },

        async action(env, type) {
            if (!confirm(`Are you sure you want to trigger a ${type} for ${env}?`)) return;
            
            this.environments[env].status = type === 'deploy' ? 'deploying' : 'restarting';
            this.environments[env].version = '--';
            
            try {
                const endpoint = type === 'deploy' ? `/api/deploy/${env}` : `/api/restart/${env}`;
                await fetch(endpoint, { method: 'POST' });
                this.environments[env].status = 'healthy';
                this.fetchDeployments();
            } catch (err) {
                console.error("Action error:", err);
                this.environments[env].status = 'error';
            }
        }
    }));
    
    Alpine.data('loaddatarun', () => ({
        logs: 'Select an environment to view logs...\n',
        selectedEnv: new URLSearchParams(window.location.search).get('env') || 'dev',
        
        init() {
            if (this.selectedEnv) {
                this.fetchLogs();
                setInterval(() => this.fetchLogs(), 3000);
            }
        },
        
        async fetchLogs() {
            try {
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                const res = await fetch(`/api/logs/${this.selectedEnv}?tz=${tz}`);
                const data = await res.json();
                if (data.status === 'success') {
                    this.logs = data.logs;
                    this.$nextTick(() => {
                        const term = document.getElementById('terminal-content');
                        if(term && term.scrollHeight - term.scrollTop === term.clientHeight) {
                            term.scrollTop = term.scrollHeight;
                        } else if(term && this.logs.length < 500) {
                            term.scrollTop = term.scrollHeight;
                        }
                    });
                } else {
                    this.logs = `Error fetching logs: ${data.message}`;
                }
            } catch(e) {
                this.logs = 'Failed to connect to backend api.';
            }
        }
    }));
});
