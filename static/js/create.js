let create_book = new Vue({
    el: '#create_book',
    data:{
        book_name: '',
        digest: '',
        auth: '',
        msg: '',
        error: '',
        tags: [],
        selected_tag_id: null,
    },
    mounted(){
        this.get_auth();
        this.get_tags();
    },
    methods:{
        get_tags(){
            axios.get("/api/tags/").then(res => {
                if (res.data.success){
                    this.tags = res.data.data;
//                    console.log(this.tags);
                }else{
                    this.error = `获取标签失败： ${res.data.msg}`
                }
            })
        },
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
            axios.post('/api/books/', {"book_name": this.book_name, "digest": this.digest, "tag_id": this.selected_tag_id}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.msg = res.data.msg;
                    } else {
                        this.error = '创建书籍失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {flash_msg(e.response?e.response.data.msg:e,false);})
        },
}});

let create_content = new Vue({
    el: '#create_content',
    data:{
        books: [],
        book_id: '',
        chapter: '',
        content: '',
        book_id: '',
        msg: '',
        error: '',
        free: true,
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
            }).catch(e => {flash_msg(e.response?e.response.data.msg:e,false);})
        },
        select_book(book_id){
            this.book_id = book_id;
        },
        commit(){
            this.error = '';
            this.msg = '';
            axios.post(`/api/content/create_content/${this.book_id}`,
             {"chapter": this.chapter, "content": this.content, "free": this.free},
              {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        flash_msg(res.data.msg);
                    } else {
                        flash_msg(`提交失败：${res.data.msg || '未知错误'}` )
                    }
            }).catch(e => {flash_msg(e.response?e.response.data.msg:e,false);})
        },
}});