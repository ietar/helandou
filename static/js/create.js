let create_book = new Vue({
    el: '#create_book',
    data:{
        book_name: '',
        digest: '',
        auth: '',
        msg: '',
        error: '',
    },
    mounted(){
        this.get_auth();
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        commit(){
            this.error = '';
            this.msg = '';
            axios.post('/api/books/', {"book_name": this.book_name, "digest": this.digest}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.msg = res.data.msg;
                    } else {
                        this.error = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {
                this.error=e.response.data.msg;
                console.log(this.error);
//                alert(this.error);
            })
        },
}});

let create_content = new Vue({
    el: '#create_content',
    data:{
        books: [],
        book_id: '',
        chapter_order: '',
        chapter: '',
        content: '',
        book_id: '',
        msg: '',
        error: '',
    },
    mounted(){
        this.get_auth();
        this.get_my_books();
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        get_my_books(){
            axios.get('/api/books/my_books', {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                    this.books = res.data.data;
                }
            }).catch(e => {console.log(e)})
        },
        select_book(book_id){
            this.book_id = book_id;
        },
        commit(){
            this.error = '';
            this.msg = '';
            axios.post(`/api/content/create_content/${this.book_id}`,
             {"chapter_order": this.chapter_order, "chapter": this.chapter, "content": this.content},
              {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.msg = res.data.msg;
                    } else {
                        this.error = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {
                this.error=e.response.data.msg;
                console.log(this.error);
//                alert(this.error);
            })
        },
}});