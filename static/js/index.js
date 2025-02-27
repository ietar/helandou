function f1(){
    let form = document.getElementById('drawcards');
    let fd = new FormData(form);
    let xhr = new XMLHttpRequest();
    xhr.open('post', '/drawcards/');
    xhr.send(fd);
    xhr.onreadystatechange = function(){
        if(4 === xhr.readyState){
            if (xhr.status === 200 || xhr.status === 304){
                let ret = JSON.parse(xhr.responseText);
                document.getElementById('draw_result').innerHTML = ret.length;
            }
        }
    }
}
function f2(){
    let iframe = document.getElementById('iframe1');
    iframe.src = "/drawcards/";
    iframe.width = 660;
    iframe.height = 150;
}
function f3(){
    let iframe = document.getElementById('iframe1');
    iframe.src = "";
    iframe.width = 0;
    iframe.height = 0;
}
// $(function () {
//     let buttons = $('div.header>div.container>div');
//     buttons.mouseenter(function () {
//         $(this).find('div').slideDown(300);
//     });
//     buttons.mouseleave(function () {
//         // console.log('trying:', $(this).find('div'));
//         $(this).find('div').slideUp(100);
//     })
// });

