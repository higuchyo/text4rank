//adjust footer bottom
function ct() {
	return document.compatMode == "BackCompat" ? document.body.clientHeight : document.documentElement.clientHeight;
}
var f = document.getElementById('footer');
(window.onresize = function () {
		f.style.position = document.body.scrollHeight > ct() ? '' : 'absolute';
})();

// search event
	// click search btn
$('#searchBtn').click(function() {
	search()
});
	// press enter
$('#inputFieldAddress').keydown(function(e){
	if (e.keyCode == 13) {
	 search()
	}
});
// press enter
$('#inputFieldQuery').keydown(function(e){
if (e.keyCode == 13) {
 search()
}
});

	// select value from dropdown-menu
$('.dropdown-menu a').click(function(){
  $(this).parents('.btn-group').find('.dropdown-toggle').html($(this).text()+'<span></span>');
  $(this).parents('.btn-group').find('input[name="dropdown-value"]').val($(this).attr("data-value"));
});

// go backend to search
function search() {
	var a = $('#inputFieldAddress').val();
	var q = $('#inputFieldQuery').val();
	var max_num = $('#maxNum').val();

	if (max_num == "") {
		max_num=20;
	}

	if (q == "" || q == null || q == undefined) {
		location.href='/';
	} else {
		//parse special char
		var  entry = { "'": "&apos;", '"': '&quot;', '<': '&lt;', '>': '&gt;' };
		a = a.replace(/(['")-><&\\\/\.])/g, function ($0) { return entry[$0] || $0; });
		q = q.replace(/(['")-><&\\\/\.])/g, function ($0) { return entry[$0] || $0; });

		var string = '/query?a='+a+'&q='+q+'&max_num='+max_num;
		location.href = string;
	};

}
