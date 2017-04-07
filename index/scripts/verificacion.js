function validarpais () {

	var x = document.getElementById("pais").value
	x = x.toUpperCase();//Hacemos mayúscula la primera letra
	var paises = ["ESPAÑA", "FRANCIA", "ITALIA", "PORTUGAL", "RUSIA", "SUIZA", "FINLANDIA", "ALEMANIA", "POLONIA", "TURQUIA"]
	var posicion = paises.indexOf(x);//Devuelve la posicion del nombre del país en la cadena
    if (posicion > -1) {//Si la posicion es 0 o mayor es que existe en la lista
       // alert("País correcto")
    } else if(document.getElementById("pais").value!=""){//Para que no nos mande el mensje si no hemos escrito nada
    	document.getElementById("pais").value = "";
    	var element = document.getElementById("pais");
        element.focus();//volver a poner el focus en el elemento. No funciona en firefox por algún motivo
        alert("Introduzca un nombre de país válido")
    }
}

var error=false
function validartemperatura(){

	var temperaturamax = document.getElementById("tempmax").value
	var temperaturamin = document.getElementById("tempmin").value
	var diferencia = temperaturamax-temperaturamin

	if((diferencia<26 || diferencia>28) && error==false)
	{
		error=true//Así el error solo nos salta una vez
		alert("Temperatura erronea , la diferencia de temperatra debe estar entre 26 y 28ºC");
		document.getElementById("resultado").style.color="red";
	}
	else if(diferencia>=26 && diferencia<=28){
		error=false
	 	document.getElementById("resultado").style.color="black";}

}

function validarpass(){
	var contr = document.getElementById("contraseña").value;
	if(contr.length<5)
	{
		document.getElementById("calidadpass").innerHTML="Contraseña débil";
		document.getElementById("calidadpass").style.color="red";
	}
	else  if(contr.length>5 && contr.length<10){
		document.getElementById("calidadpass").innerHTML="Contraseña media";
		document.getElementById("calidadpass").style.color="orange";
	}
	else  if(contr.length>=10){
		document.getElementById("calidadpass").innerHTML="Contraseña buena";
		document.getElementById("calidadpass").style.color="green";
	}
	}

function validarpass2(){
	if(document.getElementById("contraseña").value.length<=5)
	{
		alert("Contraseña débil, introduzca una contraseña con más caracteres.")
		document.getElementById("contraseña").value="";//para vaciar el campo de la contraseña porque no es válida
	}
	}

function generarenlace(){
   var coord=document.getElementById("coordenadas").value;
   var enlace = "https://maps.google.com/maps?q="+coord;
   document.getElementById("mapa").value=enlace;
   document.getElementById("enlace").href=enlace;//hacemos que el botón ir nos lleve al enlace obtenido
}

function validarEmail() {
	var mail = document.getElementById("email").value
	var regexp=/^([a-zA-Z0-9]+[-\._]?)+\@[a-zA-Z0-9]+(\.([a-zA-Z]{2,4}))+$/ 
	if(mail=="") 
		{return}
	if ( !regexp.test(mail)){
	    alert("Error: La dirección de correo " + mail + " es incorrecta.");
	}
	else if ( regexp.test(mail)){
    	alert("La dirección de correo " + mail + " es correcta.");
	}
}
