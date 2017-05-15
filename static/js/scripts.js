var timeout_ajax = 20000
/* Evento click en el boton compuesto de cantidad item
 * Este boton sirve para aumentar y disminuir las cantidades de un item
 * De manera automatica actualiza el input sumando o restando una unidad y
 * actualiza el campo data-target que contenga ese input
 */
$("i[data-role=aumentar],i[data-role=disminuir]").click(function()
{
    var data_role = $(this).attr('data-role')
    // Se carga el objeto input donde se debe visualizar la cantidad
    campo_input = $(this).siblings("input:not(:hidden)")
    // Se obtiene la cantidad actual del campo_input
    var cantidad_actual = parseInt($(campo_input).val())
    var cantidad = 0
    // Se aumenta la cantidad
    if(data_role == 'aumentar'){
        cantidad = cantidad_actual + 1
    }
    else {
        // Se disminuye la cantidad
        cantidad = cantidad_actual -1
        // la cantidad no puede ser menor a 1
        if(cantidad <= 0){
          cantidad = 1
          return;
        }
    }
    // Asignamos la cantidad calculada al campo input
    $(campo_input).val(cantidad)
    // obtenemos el campo_target (donde se visualizará el valor total)
    campo_target = $(campo_input).attr('data-target')
    if(!jQuery.isEmptyObject(campo_target)){
      var valor_unitario = parseInt($(campo_target).html().replace(/\./g,'').replace(/\$/g,'')) / cantidad_actual
      var valor_total = cantidad*valor_unitario
      $($(campo_input).attr('data-target')).html(format_currency(valor_total))
    }

    // Si contiene un hermano input type=hidden e id^='idSaldoInventario' se debe ajustar el carrito
    // esta funcionalidad es para cuando el usuario esta en la vista del cart
    var campo_saldo = $(this).siblings("input[type=hidden][id^='idSaldoInventario']")
    if(campo_saldo.length > 0){
      var campo_saldo = $(this).siblings("input[type=hidden][id^='idSaldoInventario']")
      var idSaldoInventario = $(campo_saldo).val()
      
      add_to_cart($(campo_saldo).attr('src-url').replace('-1',cantidad))
      //add_to_cart("/cart/change/"+idSaldoInventario+"/"+cantidad+"/")
    }
});
/* Solo para (button) con atributos data-target y src-url
 * Carga mediante ajax en un modal el contenido de una url proporcionada en atributo src-url 
 * Revisar documentación Bootstrap => Modal
 * Parametros:
 * data-target: modal donde se cargará el contendio
 * src-url: url del contenido a cargar mediante ajax
 * data (opcional): datos GET (data="param1=value1&param2=34")
 * Ejemplo: <button type="button" data-toggle="modal" data-target="#myModal" src-url="ajax/test.html" data="param1=value1&param2=34"></button>
 */
$(document).on('click',"button[data-toggle='modal'][src-url]",function()
{
    // Cargamos en el data-target, el contenido de la src-url pasando los parametros GET data
    $($(this).attr('data-target')).load($(this).attr('src-url'),$(this).attr('data'))
});
// carga en un select el resultado de una json mediante ajax
// Formato del json
// {"items": [{"value": 1, "description": "descripcion 1"},{"value": 2, "description": "descripcion 2"}]}
// Parametros
// url: url del json
// objeto: select al cual se va a cargar los options
// value: el valor que se le debe asignar al select (solo si es necesario)
function load_options_select(url,objeto,value = null)
{
  getJSON(url,function(data){
    var options = "<option value='0'>---</option>"
    $.each(data.items,function(i,option)
    {
        options += "<option value='"+option.value+"'>"+option.description+"</option>"
    })
    $(objeto).html(options)
    // Se asigna el valor al select
    if(value != null)
        $(objeto).val(value)
  });
}
// Redireccionamiento
function redirect(url){
    $(location).attr('href',url)
}
// Agrega un elemento al carro mediante ajax
// la vista devuelve un json y este es cargado al objecto correspondiente ".badge-count-cart"
// url: es la url de la vista de adicion al carro, esta debe
//      proporcionarse desde la vista con el parametro de id y cantidad "/cart/add/id/cantidad/" 
function add_to_cart(url){
  getJSON(url,function(data){
    /* se carga la cantidad total en los elementos 
       que tengan como clase cantidad-total-carro
       y el valor total en los elementros con clase valor-total-carro */
    $(".cantidad-total-carro").html(data.cart.cantidad_total)
    $(".valor-total-carro").html(format_currency(data.cart.valor_total))
  })
}
function getJSON(url,success,options=null){
  return $.ajax({
            dataType: "json",
            url: url,
            data: options!=null? options.data || null: null,
            method: options != null? options.method || "GET":"GET",
            beforeSend:options!=null? options.beforeSend || null: null,
            success: success,
            error: function(jqXHR,estado,error){
              console.log(error);
              console.log(estado);
            },
            timeout:timeout_ajax //tiempo maximo de espera
          });
}
// Se usa en el index
// agregan asincronamente los productos a un objeto
function cargar_productos_asincrono(URL,objeto,datos){
    $.ajax(
    {
        async: true,
        type: "GET",
        url: URL,
        data: datos,
        success: function(resp){
            if(resp.length > 0){
                $(objeto).append(resp);
            }
            else
              $(objeto).remove()
        },
        error: function(jqXHR,estado,error){
            console.log(error);
            console.log(estado);
        },
        timeout:timeout_ajax //tiempo maximo de espera
    });
}
// funcion para usar ajax
// URL : url 
// objeto : #id o .class del objeto donde se va a cargar el resultado de la petición
// datos : datos ejemplo 'campo = 1','blabla = 3'.......
// method : metodo por el cual se hará la petición al servidor
function usar_ajax(URL,objeto,datos,method = "POST")
{	
    $.ajax(
    {
        beforeSend: function(){
           //codigo q se ejecutará antes de q se inicie ajax;
        },
        async: true,
        type: method,
        url: URL,
        data: datos,
        success: function(resp){
            //recibe la la respuesta de ajax 
            $(objeto).html(resp);//mostramos la respuesta en el objeto	
            //console.log(resp);
        },
        error: function(jqXHR,estado,error){
            console.log(error);
            console.log(estado);
        },
        complete: function(jqXHR,estado)
        {
            //se ejecuta despues de succes o error
            console.log(estado);
        },
        timeout:timeout_ajax //tiempo maximo de espera
    });
}
// Configuración los mensajes toastr
toastr.options = {
  "closeButton": true,
  "debug": false,
  "newestOnTop": false,
  "progressBar": false,
  "positionClass": "toast-top-right",
  "preventDuplicates": true,
  "onclick": null,
  "showDuration": "500",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
}
// variable de idioma español para los DataTables
var lenguage_spanish = {
    "sProcessing":     "Procesando...",
    "sLengthMenu":     "Mostrar _MENU_ registros",
    "sZeroRecords":    "No se encontraron resultados",
    "sEmptyTable":     "Ningún dato disponible en esta tabla",
    "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
    "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
    "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
    "sInfoPostFix":    "",
    "sSearch":         "Buscar:",
    "sUrl":            "",
    "sInfoThousands":  ",",
    "sLoadingRecords": "Cargando...",
    "oPaginate": {
        "sFirst":    "Primero",
        "sLast":     "Último",
        "sNext":     "Siguiente",
        "sPrevious": "Anterior"
    },
    "oAria": {
        "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
        "sSortDescending": ": Activar para ordenar la columna de manera descendente"
    }
}
/*
 * Retora formato de moneda
 */
function format_currency(value){
  return "$"+parseInt(value).toString().replace(/(\d)(?=(\d{3})+$)/g, "$1.")
}

//<== funcion que captura un parametro GET ===>
(function($) {  
    $.get = function(key)   {  
        key = key.replace(/[\[]/, '\\[');  
        key = key.replace(/[\]]/, '\\]');  
        var pattern = "[\\?&]" + key + "=([^&#]*)";  
        var regex = new RegExp(pattern);  
        var url = unescape(window.location.href);  
        var results = regex.exec(url);  
        if (results === null) {  
            return null;  
        } else {  
            return results[1];  
        }  
    }  
})(jQuery);

$(document).ready(function(){
  // Add smooth scrolling to all links in navbar + footer link
  $(window).scroll(function(){
      if ($(this).scrollTop() > 120) $('.to-top').fadeIn();
      else $('.to-top').fadeOut();
  });
  $(".navbar a, footer a[href='#myPage']").on('click', function(event) {
    // Make sure this.hash has a value before overriding default behavior
    if (this.hash !== "") {
      // Prevent default anchor click behavior
      event.preventDefault();

      // Store hash
      var hash = this.hash;

      // Using jQuery's animate() method to add smooth page scroll
      // The optional number (900) specifies the number of milliseconds it takes to scroll to the specified area
      $('html, body').animate({
        scrollTop: $(hash).offset().top
      }, 900, function(){

        // Add hash (#) to URL when done scrolling (default click behavior)
        window.location.hash = hash;
      });
    }
  });

  /* ANIMACIÓN AL BUTTON SEARCH */
  var altoHeader = $("#navbar-principal").height();
  $(".container-fixed-top").css("padding-bottom",altoHeader+"px");

  //al darle click a button search
  if (screen.width<991) 
  {
    $('#buttonsearch').click(function(){
      //se le aplica a forms de search un metodo llamado slideToogle que es una animacion que permite que el elemento suba y baja.
      $('#formsearch').slideToggle("fast",function(){
          $('#buttonsearch').hide("fast");
      });
      //se hace focus en input text el icono de busqueda se reemplaza por el indicado dando cambio a su estado de display none, con el metodo toogle entre ocultar y mostar el elmento seleccionado 
      $('#searchbox').focus();
    });
    $('#searchbox').blur(function(){
      $('#formsearch').hide("fast");
      $('#buttonsearch').css("display","block");
    });
  }
  else
  {
    $('#formsearch').css("display","block");
    $('#buttonsearch').hide("fast");
  };

  setTimeout(function() {
    $(".alert").fadeOut(1500);
  },3000);
});
$.ajaxPrefilter(function( options, original_Options, jqXHR ) {
    options.async = true;
});
(function(a) {
    a.fn.validarCampo = function(options) {
    switch(options.type){
      case 'number':
        characters = '0123456789'
        break;
      case 'char':
        characters = 'abcdefghijklmnñopqrstuvwxyzáéíóú '
        break;
      default:
        characters = "0123456789abcdefghijklmnñopqrstuvwxyzáéíóúABCDEFGHIJKLMNÑOPQRSTUVWXYZÁÉÍÓÚ "
        break;
    }
        max_length = options.length || null;
        a(this).on({
            keypress: function(a) {
              if(max_length == null || $(this).val().length <= max_length-1){
                
                  var c = a.which,
                      d = a.keyCode,
                      e = String.fromCharCode(c).toLowerCase(),
                      f = characters;
                  (-1 != f.indexOf(e) || 9 == d || 37 != c && 37 == d || 39 == d && 39 != c || 8 == d || 46 == d && 46 != c) && 161 != c || a.preventDefault()
              }
              else
                a.preventDefault();
            }
        })
    }
})(jQuery);