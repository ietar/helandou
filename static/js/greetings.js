let greet = new Vue({
    el: '#greetings',
    data:{
        counts: 0,
        latest: null,
        auth:'',
        error_msg:'',
        error_free_msg:'',
    },
    mounted(){
        this.get_auth();
        this.greet()
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        greet(){
            axios.get('/api/user/greet', {headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                    this.counts = res.data.data.counts;
                    this.latest = res.data.data.latest;
                }
            }).catch(e => {console.log(e)})
        },
        vivo50(){
            if(!this.auth){
                this.error_msg = '未登录';
                this.error_free_msg = '';
            }
            else{
                axios.post(`/api/user/vivo50`,{},{headers:{'Authorization': this.auth}, responseType: 'json'})
                .then(res => {
                    if (res.data.success) {
                        this.error_free_msg = `领到了${res.data.data.amount}`;
                        this.error_msg = '';
                    } else {
                        this.error_msg = res.data.msg || '未知错误';
                        this.error_free_msg = '';
                    }
                }).catch(e => {
                    this.error_msg=e.response.data.msg || e;this.error_free_msg = '';
                })
            }
}}});
