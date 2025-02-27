let search_books = new Vue({
    el: '#search_result',
    data:{
        books: [],
        count: 0,
        auth: '',
        error: ''
    },
    mounted(){
        this.get_auth();
        this.get_books()
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

            const urlParams = new URLSearchParams(window.location.search);
            const q = urlParams.get('q') || '';
            axios.get('/api/books/search',{params:{"q":q}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                    this.books = res.data.data;
                    this.count = this.books.length?this.books.length:0;
                } else {
                    this.error = '数据加载失败：' + (res.data.msg || '未知错误')
                }
            }).catch(e => {console.log(e)})
        }
}});