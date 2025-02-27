let ap_books = new Vue({
    el: '#content',
//    delimiters: ['[[', ']]'],
    data:{
        book_id: '',
        book_name: '',
        chapter_order: '',
        last_chapter_order: '',
        next_chapter_order: '',
        error_msg: '找不到该书',
        content: '',
        comments: [],
        comment_to_send: ''
    },
    mounted(){
        this.get_auth(),
        this.get_content(),
        this.get_comments()
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        add_collections(){
            axios.post('/api/content/add_to_collection', {"content_id": this.content.id}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    alert(res.data.msg)
                }
            })
        },
        get_content(){
            let u = window.location.href;
            const regex = /\/books\/(\d+)\/(\d+)(?:\/|$|#|\?)/;
            const match = u.match(regex);
            if (!match){alert("找不到该内容")}
            this.book_id = parseInt(match[1], 10);
            this.chapter_order = parseInt(match[2], 10);
            this.last_chapter_order = this.chapter_order -1;
            this.next_chapter_order = this.chapter_order +1;

            axios.get(`/api/content/${this.book_id}/${this.chapter_order}`,{params:{},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.content = res.data.data;
                        this.book_name = res.data.data['book_name'];
//                        console.log(this.content);
                    } else {
                        this.error_msg = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {console.log(e)})
        },
        get_comments(){
            axios.get(`/api/comment/get_all_comments/${this.book_id}/${this.chapter_order}`,{params:{},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.comments = res.data.data;
                    } else {
                        this.error_msg = '数据加载失败：' + (res.data.msg || '未知错误')
                    }
            }).catch(e => {console.log(e)})
        },
        add_comment(){
            axios.post(`/api/comment/create_comment/${this.book_id}/${this.chapter_order}`,
             {"content": this.comment_to_send}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    console.log(res.data.msg);
                    this.comment_to_send = '';
                    this.get_comments();
                }
            })
        },
        agree(comment_id){
            axios.post(`/api/comment/agree/${comment_id}`, {}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    console.log(res.data.msg);
                    this.get_comments();
                }
            })
        },
}});