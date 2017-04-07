function guardardatos(){
      var Datos = {Pais: "",Ciudad: "", Coordenadas:"", Mapa: "", Foto: "", Contraseña: "", Temperatura: false, Humedad: false, Sonido: false, Luz: false, Movimiento: false, Tempmax: 0, Tempmin: 0};
      if(typeof(Storage)!=="undefined") 
      {
        Datos.Pais = document.getElementById("pais").value;
        Datos.Ciudad = document.getElementById("ciudad").value;
        Datos.Coordenadas = document.getElementById("coordenadas").value;
        Datos.Mapa = document.getElementById("mapa").value;
        Datos.Foto = document.getElementById("foto");
        Datos.Contraseña = document.getElementById("contraseña").value;
        Datos.Temperatura = document.getElementById("temperatura");
        Datos.Humedad = document.getElementById("humedad");
        Datos.Sonido = document.getElementById("sonido");
        Datos.Luz = document.getElementById("luz");
        Datos.Movimiento = document.getElementById("movimiento");
        Datos.Tempmax = document.getElementById("tempmax").value;
        Datos.Tempmin = document.getElementById("tempmin").value;
        //alert(Datos.Pais + Datos.Ciudad + Datos.Coordenadas + Datos.Mapa + Datos.Foto + "\n" + Datos.Contraseña + Datos.Tempmin +  Datos.Temperatura + Datos.Humedad)
        localStorage.setItem("EstructuraDatos", Datos);//guardamos la estructura en localstorage

        alert("Datos guardados en la estructura 'Datos'")
      }
    }