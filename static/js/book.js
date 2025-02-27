let ap_books = new Vue({
    el: '#book_view',
//    delimiters: ['[[', ']]'],
    data:{
        book: '',
        book_id: '',
        chapters: [],
        error_msg: '找不到该书',
    },
    mounted(){
        this.get_auth(),
        this.get_book()
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        get_book(){
            let u = window.location.href;
            const match = u.match(/\/(\d+)\/?$/);
            this.book_id = match ? parseInt(match[1], 10) : null;
            axios.get(`/api/books/${this.book_id}`,{params:{},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.book = res.data.data;
                    } else {
                        this.error_msg = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {console.log(e)})
            axios.get(`/api/content/get_all_chapters/${this.book_id}`,{params:{},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.chapters = res.data.data;
                    } else {
                        this.error_msg = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {console.log(e)})
        },

}});