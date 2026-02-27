let ap_books = new Vue({
    el: '#content',
//    delimiters: ['[[', ']]'],
    data:{
        book_id: '',
        book_name: '',
        chapter_id: '',
        error_msg: '找不到该内容',
        content: '',
        chapter_comments: [],
        to_rematch: 0,  // 将被重新关联的评论id
        new_home: -1,  // 执行关联后的paragraph 默认扔给章评

        activeParagraphIndex: null, // 控制当前展开的段落评论
        paragraph_comments: [],

        hanging_comments: [],
        comment_to_send: '',
        editing: false,
        need_subscribe:true,
        subscribe_text: '',
        can_edit: false,
    },
    mounted(){
        this.get_auth();
        this.get_content();
        this.get_comments();
    },
    methods:{
        formatTime(timestamp) {
            const date = new Date(timestamp);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        },
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
                    flash_msg(res.data.msg)
                }
            })
        },
        get_content(){
            let u = window.location.href;
            const regex = /\/content\/(\w+)/;
            const match = u.match(regex);
            this.chapter_id = parseInt(match[1], 10);

            axios.get(`/api/content/${this.chapter_id}`,{params:{},headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.content = res.data.data;
                        this.book_name = res.data.data['book_name'];
                        this.book_id = res.data.data['book_id'];
                        this.need_subscribe = res.data.data["need_subscribe"]
                        let cost = res.data.data["cost"];
                        this.subscribe_text = `消耗${cost}订阅该章节`;
                        this.can_edit = res.data.data["can_edit"]
                    } else {
                        this.error_msg = res.data.msg || '未知错误';
                    }
            }).catch(e => {console.log(e);this.error_msg = e.response.data.msg || '未知错误';})
        },
        get_comments(){
            axios.get(`/api/comment/get_all_comments/${this.chapter_id}`,{params:{},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.chapter_comments = res.data.data["chapter_comments"];
                        this.paragraph_comments = res.data.data["paragraph_comments"];
                        this.hanging_comments = res.data.data["hanging_comments"];
                    } else {
                        this.error_msg = res.data.msg || '未知错误';
                    }
            }).catch(e => {flash_msg(e, false)})
        },
        add_comment(paragraph){
            axios.post(`/api/comment/create_comment/${this.chapter_id}`,
             {"content": this.comment_to_send, "paragraph": paragraph}, {headers:{'Authorization': this.auth}, responseType: 'json'})
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
            }).catch(e => {flash_msg(e.response.data.msg, false)})
        },
        delete_comment(comment_id){
            axios.delete(`/api/comment/${comment_id}`,{headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
//                    console.log(res.data.msg);
                    this.get_comments();
                }
            }).catch(e => {flash_msg(e.response.data.msg, false)})
        },
        edit_content(){
            this.editing = !this.editing;
            const fullContent = document.getElementById('full_content');
            const newFullContent = document.getElementById('new_full_content');
            if (fullContent && newFullContent) {
                const width = fullContent.offsetWidth;
                newFullContent.style.width = width + 'px';
            }
        },
        put_content(){
            axios.put(`/api/content/${this.chapter_id}`, {"chapter": this.content.chapter, "content": this.content.content},
             {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    flash_msg(res.data.msg);
                    this.editing = false;
                }
            }).catch(e => {flash_msg(e.response.data.msg, false)})
        },
        subscribe(){
            axios.post(`/api/content/subscribe/${this.content.id}`, {}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    flash_msg(res.data.msg);
                    this.get_content();
                }
            }).catch(e => {flash_msg(e.response.data.msg, false)})
        },
        getParagraphComments(index) {
            return this.paragraph_comments[index.toString()] || [];
        },
        // 切换段落评论显示
        toggleParagraphComments(index) {
            if(this.activeParagraphIndex == -2 && index != -2 && this.hanging_comments.length != 0){
//                flash_msg('重新关联模式' + this.hanging_comments, this.hanging_comments.length);
                this.new_home = index;
                return
            }
            this.activeParagraphIndex = this.activeParagraphIndex === index ? null : index;
        },
        // 获取段落评论数量
        getParagraphCommentCount(index) {
            return this.getParagraphComments(index)?.length || 0;
            return this.paragraph_comments[index]?.length || 0;
        },
        // 获取指定段落的评论列表
        getParagraphComments(index) {
            if(index == -1){return this.chapter_comments};
            if(index == -2){return this.hanging_comments};
            return this.paragraph_comments[index] || [];
        },
        formatDigest(digest){
            if(digest == null){return ''};
            if(digest.length == 20){
                return digest.slice(0,10) + "..." + digest.slice(10);
            }
            else{
                return digest;
            }
        },
        choose_one(one){
            this.to_rematch = one;
        },
        rematch(){
            axios.post(`/api/comment/rematch_comment/${this.to_rematch}`, {"new_paragraph": this.new_home}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    flash_msg(res.data.msg)
                    this.get_comments();
                }
            }).catch(e => {flash_msg(e.response.data.msg), false})
        }
}});