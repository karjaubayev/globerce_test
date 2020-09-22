menubar = false;
showButton = document.getElementById("show");
hideButton = document.getElementById("hide");
menu = document.getElementById("menu_bar");

function openMenu(){
	if (!menubar) {
		menu.style.width = "600px";
		showButton.style.display = 'none';
		hideButton.style.display = 'block';
		menubar = true;
	}else {
		menubar = false
		showButton.style.display = 'block';
		hideButton.style.display = 'none';
		menu.style.width = "0px";
	}
}
function myFunction() {
  var dropdowns = document.getElementById("myDropdown");
  if (dropdowns.classList.contains('show')) {
    dropdowns.classList.remove('show');
  }else {
  	dropdowns.classList.toggle("show")
  }
}

function dropTitle(value) {
	element = document.getElementById("dropTitle");
	if(value==1){
		element.innerHTML = 'ТЭЦ-1';
	}else if(value==2){
		element.innerHTML = 'ТЭЦ-2';
	}else if(value==3){
		element.innerHTML = 'ТЭЦ-3';
	}else {
		element.innerHTML = 'СУММАРНО';
	}
	var dropdowns = document.getElementById("myDropdown");
      if (dropdowns.classList.contains('show')) {
        dropdowns.classList.remove('show');
      }
	
}	
