let ap_books = new Vue({
    el: '#app',
    data:{
        id:'',
        username: '',
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

    },
    mounted(){
        this.get_auth();
        this.get_my_info();
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
        get_my_info(){
            if (document.cookie != ''){
                let user = JSON.parse(window.atob(document.cookie.split(".")[1]));
                this.id = user.id;
                axios.get(`/api/user/${this.id}`,{headers:{'Authorization': this.auth}, responseType: 'json'})
                    .then(res => {
                        if(res.data.success){
                            this.username = res.data.data.username;
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
                this.error_msg = "未登录";
                return
            }
        },
        edit(){
//            $('#email').attr('disabled', false);
//            $('#mobile').attr('disabled', false);
            $('#email').prop('disabled', !$('#email').prop('disabled'))
            $('#mobile').prop('disabled', !$('#mobile').prop('disabled'))
            $('#former_password').prop('disabled', !$('#former_password').prop('disabled'))
            $('#new_password').prop('disabled', !$('#new_password').prop('disabled'))
        },
        save(){
            let params = {"former_password": this.former_password,
            "new_password": this.new_password,
            "email":this.email,
            "mobile":this.mobile};
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