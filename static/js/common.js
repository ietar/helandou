const LevelEnum = {
    unvalidated: 1,
    normal: 2,
    admin: 5,
    root: 10
}

function deleteCookie(name) {
    // 设置一个过去的时间点作为过期时间
    let expires = "expires=Thu, 01 Jan 1970 00:00:00 GMT";
    // 构造要设置的Cookie字符串，注意这里value为空，且不需要设置path等属性（除非原来设置了）
    document.cookie = name + "=; " + expires;
}


let app = new Vue({
    el: '#user_info_bar',
    delimiters: ['[[', ']]'],
    data:{
        username: '',
    },
    mounted(){
        let path = encodeURIComponent(window.location.pathname);
        let href = `/user/login?from=${path}`;
        document.getElementById('login').href = href;
        if (document.cookie != ''){
            let user = JSON.parse(window.atob(document.cookie.split(".")[1]))
            this.username = user.username;
    //        logout = document.getElementById("logout");
    //        logout.addEventListener("click", function(){
    //            this.username = "";
    //            deleteCookie("Authorization");
    //            location.reload()}
    //        );
    }
    },
});

let app2 = new Vue({
    el: '#search_bar',
    delimiters: ['[[', ']]'],
    data:{
        search_place_holder: '',
    },
    mounted(){
        this.get_anything()
    },
    methods:{
        get_anything(){
            axios.get('/anything',{params:{},headers:{'X-CSRFToken': this.csrf}, responseType: 'json'})
            .then(res => {
                this.search_place_holder = res.data.data['search_place_holder'];
                // console.log(res.data);
            }).catch(e => {console.log(e)})
        }
    }
});

