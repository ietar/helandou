let ap_books = new Vue({
    el: '#books',
    delimiters: ['[[', ']]'],
    data:{
        books: [],
        collections: [],
        auth: '',
    },
    mounted(){
        this.get_auth();
        this.get_books()
        this.get_my_collections()
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        get_books(){
            axios.get('/api/books/',{params:{},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.books = res.data.data;
                    } else {
                        this.error = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {console.log(e)})
        },
        delete_collection(content_id){
            axios.post('/api/content/add_to_collection', {"content_id": content_id}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
//                    window.location.reload();
                    this.get_my_collections();
                }
            })
        },
        get_my_collections(){
            axios.get('/api/content/my_collections', {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                    this.collections = res.data.data;
//                    console.log(this.collections);
                }
            }).catch(e => {console.log(e)})
        },
}});