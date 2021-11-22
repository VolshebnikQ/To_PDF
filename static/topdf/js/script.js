//Листать чат в самый низ
function scroll(){
    if(document.getElementById("pageChat")){
        document.getElementById("Chat").scrollTo(0,document.getElementById("Chat").scrollHeight)
    }
}
//Обновление страницы каждую (time = 1000) секунду 
function reload_interval(time){
	setTimeout(function(){
		location.reload();
	}, time);
}