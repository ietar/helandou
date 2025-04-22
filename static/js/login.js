let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        from: '',
        image_code_url: '',
        uuid: '',
        image_code: '',
        username: '',
        password: '',

        error_img_code: true,
        error_password: true,

        error_img_message: '',
        show_success: false,
        success_message: '',

        error_login_message: '',
        error_login: false,

    },
    mounted(){
//        this.csrf = $('input[name=csrfmiddlewaretoken]').val();
        this.generate_image_code();
    },
    methods: {
        generate_image_code(){
            this.uuid = guid();
            $('input#uuid').val(this.uuid);
            this.image_code_url = `/image_codes/${this.uuid}`;
        },
        check_img_code(){
            if (this.image_code.length !== 4){
                this.error_img_message = "请输入图形验证码";
                this.error_img_code = true;
                return false
            }
            else{
                this.error_img_code = false;
            }
            let url = `/get_image_code_by_uuid/${this.uuid}`
            axios.get(url)
                .then(response => {
                    if (response.data.success === true){
                        if (response.data.data.code === this.image_code){
                            this.error_img_code = false;
                        }
                        else{
                            this.error_img_code = true;
                            this.error_img_message = '请输入正确的图形验证码'
                        }
                    }
                    else{
                        this.error_img_code = true;
                        this.error_img_message = '图形验证码过期';
                    }
                }).catch(e => console.log(e))
        },
        check_password(){
            let re = /^[a-zA_Z0-9-_@]{8,20}$/;
            this.error_password = !re.test(this.password);
        },
        forget_password(){
            window.location = '/user/forget_password';
        },
        on_submit(e){
            this.check_img_code();

            if (this.error_password === true || this.error_img_code === true){
                // window.event.returnValue = false;
                e.preventDefault();
                return;
            }
            else{
                let searchParams = new URLSearchParams(window.location.search);
                let from = searchParams.get('from');
                from = from?from:"/";
                this.from = from;

                e.preventDefault();
                let url = `/api/user/login`;
                axios({
                    url: url,
                    method: 'post',
                    data: {
                    'username': this.username,
                    'password': this.password,
                    'uuid': this.uuid,
                    'image_code': this.image_code,
                    },
                    headers: {
                        'Content-Type':'application/json',
                        // 'Content-Type':'application/x-www-form-urlencoded',
                        // 'X-CSRFToken': window.sessionStorage.getItem("csrf_token")
//                        'X-CSRFToken': this.csrf,
                    }})
                    .then(response => {
                        if (response.data.success === true) {
                            // 显示成功提示
                            this.show_success = true;
                            this.countdown = 3;  // 初始化倒计时
                            this.success_message = `注册成功，${this.countdown}秒后自动跳转至上页面...`;
                            // 更新倒计时显示
                            const timer = setInterval(() => {
                                this.countdown -= 1;

                                // 更新提示文本
                                this.success_message = `注册成功，${this.countdown}秒后自动跳转至上页面...`;
                                document.title = `(${this.countdown})登陆成功 - ${this.username}`

                                if (this.countdown <= 0) {
                                    clearInterval(timer);
//                                    let from = from ? decodeURIComponent(from).replace(/^\//, '') : null
                                    window.location.href = from;
                                }
                            }, 1000);
                        }
                        else{
                            this.error_login = true;
                            this.error_login_message = response.data.msg;
                        }
                    }).catch(e => {
                        this.error_login = true;
                        this.error_login_message = e.response.data.msg;
                        });
            }
        },

    }
});
