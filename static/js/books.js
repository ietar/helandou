let ap_books = new Vue({
    el: '#books',
    delimiters: ['{{', '}}'],
    data:{
        tags: [],
        books: [],
        collections: [],
        auth: '',
        selected_tag_id: null,
    },
    mounted(){
        this.get_auth();
        this.get_books();
        this.get_my_collections();
        this.get_tags();
    },
    methods:{
        get_tags(){
            axios.get("/api/tags/").then(res => {
                if (res.data.success){
                    this.tags = res.data.data;
                }else{
                    flash_msg(`获取标签失败： ${res.data.msg}`,false);
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
        get_books(tag_id=null){
            axios.get('/api/books/',{params:{"tag_id": tag_id},headers:{}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                    this.books = res.data.data;
                } else {
                    this.error = '数据加载失败：' + (res.data.msg || '未知错误')
                }
            }).catch(e => {flash_msg(e, false)})
        },
        delete_collection(content_id){
            axios.post('/api/content/add_to_collection', {"content_id": content_id}, {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success){
                    this.get_my_collections();
                }
            })
        },
        get_my_collections(){
            if(!this.auth){return}
            axios.get('/api/content/my_collections', {headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                    this.collections = res.data.data;
                }
            }).catch(e => {flash_msg(e, false)})
        },
}});