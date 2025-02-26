function get_cookie(key){
    let r = document.cookie.match("\\b" + key + "=([^;]*)\\b");
    return r?r[1]:false
}

function int2ip(_int){
    _int = parseInt(_int);
    let r = [];
    for (let i=3;i>=0;i--){
        r.push((_int>>(8*i)) & 0xFF);
    }
    return r.join('.')
}

function utc2local(dateStr) {
    let date1 = new Date();
    let offsetMinute = date1.getTimezoneOffset();
    let offsetHours = offsetMinute / 60;
    let date2 = new Date(dateStr);
    date2.setHours(date2.getHours() - offsetHours);
    return date2;
}

function guid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        let r = Math.random()*16|0, v = c === 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
}

function resize(designWidth, maxWidth) {
	let doc = document,
	win = window,
	docEl = doc.documentElement,
	remStyle = document.createElement("style"),
	tid;

	function refreshRem() {
		let width = docEl.getBoundingClientRect().width;
		maxWidth = maxWidth || 1920;
		width>maxWidth && (width=maxWidth);

		let rem0 = docEl.clientWidth;
		// console.log(rem0, docEl.clientHeight, docEl.style.fontSize);
		let rem = width * 15 / designWidth;
		remStyle.innerHTML = 'html{font-size:' + rem + 'px;}';
	}

	if (docEl.firstElementChild) {
		docEl.firstElementChild.appendChild(remStyle);
	} else {
		let wrap = doc.createElement("div");
		wrap.appendChild(remStyle);
		doc.write(wrap.innerHTML);
		wrap = null;
	}
	//要等 viewport 设置好后才能执行 refreshRem，不然 refreshRem 会执行2次；
	refreshRem();

	win.addEventListener("resize", function() {
		clearTimeout(tid); //防止执行两次
		tid = setTimeout(refreshRem, 300);
	}, false);

	win.addEventListener("pageshow", function(e) {
		if (e.persisted) { // 浏览器后退的时候重新计算
			clearTimeout(tid);
			tid = setTimeout(refreshRem, 300);
		}
	}, false);

}
$(document).ready(resize(1920, 1920));
