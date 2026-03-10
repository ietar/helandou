let ap_books = new Vue({
    el: '#app',
    data:{
        id:'',
        username: '',
        coins:0,
        nickname: '',
        level:'',
        nickname_msg: '',
        last_login: '',
        login_ip: '',
        email: '',
        mobile: '',
        email_msg: '',
        mobile_msg: '',
        msg: '',
        error_msg: '',
        former_password:'',
        new_password:'',
        books: [],
        same_user: false,
    },
    mounted(){
        this.get_auth();
        this.get_user_info();
//        this.get_comments()
    },
    methods:{
        get_auth(){
            const getAuthByRegex = () => {
                const match = document.cookie.match(/Authorization=("?)(Bearer\s[\w-]+\.[\w-]+\.[\w-]+)\1/);
                return match ? match[2] : null;
                }
            this.auth = getAuthByRegex();
        },
        get_user_info(){
            if (document.cookie != ''){
                let user = JSON.parse(window.atob(document.cookie.split(".")[1]));
                this.id = user.id;

                const url = window.location.href;
                const lastSlashIndex = url.lastIndexOf('/');
                let profile_id = Number(url.substring(lastSlashIndex + 1)) || this.id;
                this.same_user = user.id == profile_id;

                axios.get(`/api/user/${profile_id}`,{headers:{'Authorization': this.auth}, responseType: 'json'})
                    .then(res => {
                        if(res.data.success){
                            this.username = res.data.data.username;
                            this.nickname = res.data.data.nickname;
                            this.level = res.data.data.level;
                            this.email = res.data.data.email;
                            this.mobile = res.data.data.mobile;
                            this.last_login = res.data.data.last_login;
                            this.login_ip = res.data.data.login_ip;
                            this.books = res.data.data.books;
                            this.coins = res.data.data.coins;
                        }
                        else{
                            alert(res.data.msg);
                        }
                    }).catch(e => {
                        this.error_msg = e.response.data.msg;
                        console.log(this.error_msg);
                    })
            }
            else{
                flash_msg("未登录,3s后跳转登录页", false);
                setTimeout(() => {
                    window.location.href="/user/login";}, 3000);
//                window.location="/user/login";
                return
            }
        },
        edit(){
//            $('#email').attr('disabled', false);
//            $('#mobile').attr('disabled', false);
            $('#email').prop('disabled', !$('#email').prop('disabled'))
            $('#nickname').prop('disabled', !$('#nickname').prop('disabled'))
            $('#mobile').prop('disabled', !$('#mobile').prop('disabled'))
            $('#former_password').prop('disabled', !$('#former_password').prop('disabled'))
            $('#new_password').prop('disabled', !$('#new_password').prop('disabled'))
        },
        save(){
            let params = {"former_password": this.former_password,
            "new_password": this.new_password,
            "email":this.email,
            "mobile":this.mobile,
            "nickname": this.nickname};
            axios.put(`/api/user/`,params,{headers:{'Authorization': this.auth}, responseType: 'json'})
            .then(res => {
                if (res.data.success) {
                        this.msg = res.data.msg;
                        this.error_msg = '';

                    } else {
                        this.error_msg = res.data.msg || '未知错误';
                        this.msg = '';
                    }
            }).catch(e => {this.error_msg=e.response.data.msg || e;this.msg = '';})
        },
}});