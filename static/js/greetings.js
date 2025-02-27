let greet = new Vue({
    el: '#greetings',
    data:{
        counts: 0,
        latest: null,
    },
    mounted(){
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
                    console.log(this.counts, this.latest);
                }
            }).catch(e => {console.log(e)})
        }
}});