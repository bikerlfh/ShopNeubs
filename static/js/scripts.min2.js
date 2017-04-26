$("i[data-role=aumentar],i[data-role=disminuir]").click(function()
{var data_role=$(this).attr('data-role')
campo_input=$(this).siblings("input:not(:hidden)")
var cantidad_actual=parseInt($(campo_input).val())
var cantidad=0
if(data_role=='aumentar'){cantidad=cantidad_actual+1}
else{cantidad=cantidad_actual-1
if(cantidad<=0){cantidad=1
return}}
$(campo_input).val(cantidad)
campo_target=$(campo_input).attr('data-target')
if(!jQuery.isEmptyObject(campo_target)){var valor_unitario=parseInt($(campo_target).html().replace(/\./g,'').replace(/\$/g,''))/cantidad_actual
var valor_total=cantidad*valor_unitario
$($(campo_input).attr('data-target')).html(format_currency(valor_total))}
var campo_saldo=$(this).siblings("input[type=hidden][id^='idSaldoInventario']")
if(campo_saldo.length>0){var campo_saldo=$(this).siblings("input[type=hidden][id^='idSaldoInventario']")
var idSaldoInventario=$(campo_saldo).val()
add_to_cart($(campo_saldo).attr('src-url').replace('-1',cantidad))}});$(document).on('click',"button[data-toggle='modal'][src-url]",function()
{$($(this).attr('data-target')).load($(this).attr('src-url'),$(this).attr('data'))});function load_options_select(url,objeto,value=null)
{$.ajax({dataType:"json",url:url,success:function(data){var options="<option value='0'>---</option>"
$.each(data.items,function(i,option)
{options+="<option value='"+option.value+"'>"+option.description+"</option>"})
$(objeto).html(options)
if(value!=null)
$(objeto).val(value)
console.log("success ")},error:function(jqXHR,estado,error){console.log(error);console.log(estado)},})}
function redirect(url){$(location).attr('href',url)}
function add_to_cart(url){$.ajax({dataType:"json",url:url,success:function(data){console.log("success "+data.cart.cantidad_total+" $"+data.cart.valor_total);$(".cantidad-total-carro").html(data.cart.cantidad_total)
$(".valor-total-carro").html(format_currency(data.cart.valor_total))},error:function(jqXHR,estado,error){console.log(error);console.log(estado)},})}
function cargar_productos_asincrono(URL,objeto,datos){$.ajax({async:!0,type:"get",url:URL,data:datos,success:function(resp){if(resp.length>0){$(objeto).append(resp)}
else $(objeto).remove()},error:function(jqXHR,estado,error){console.log(error);console.log(estado)},timeout:10000})}
function usar_ajax(URL,objeto,datos,method="POST")
{$.ajax({beforeSend:function(){},async:!0,type:method,url:URL,data:datos,success:function(resp){$(objeto).html(resp)},error:function(jqXHR,estado,error){console.log(error);console.log(estado)},complete:function(jqXHR,estado)
{console.log(estado)},timeout:10000})}
toastr.options={"closeButton":!0,"debug":!1,"newestOnTop":!1,"progressBar":!1,"positionClass":"toast-top-right","preventDuplicates":!0,"onclick":null,"showDuration":"500","hideDuration":"1000","timeOut":"5000","extendedTimeOut":"1000","showEasing":"swing","hideEasing":"linear","showMethod":"fadeIn","hideMethod":"fadeOut"}
var lenguage_spanish={"sProcessing":"Procesando...","sLengthMenu":"Mostrar _MENU_ registros","sZeroRecords":"No se encontraron resultados","sEmptyTable":"Ningún dato disponible en esta tabla","sInfo":"Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros","sInfoEmpty":"Mostrando registros del 0 al 0 de un total de 0 registros","sInfoFiltered":"(filtrado de un total de _MAX_ registros)","sInfoPostFix":"","sSearch":"Buscar:","sUrl":"","sInfoThousands":",","sLoadingRecords":"Cargando...","oPaginate":{"sFirst":"Primero","sLast":"Último","sNext":"Siguiente","sPrevious":"Anterior"},"oAria":{"sSortAscending":": Activar para ordenar la columna de manera ascendente","sSortDescending":": Activar para ordenar la columna de manera descendente"}}
$(".slider").slick({infinite:!0,centerMode:!0,slidesToShow:6,slidesToScroll:1,autoplay:!0,autoplaySpeed:1000,responsive:[{breakpoint:1024,settings:{slidesToShow:3,slidesToScroll:3,infinite:!0,}},{breakpoint:600,settings:{slidesToShow:2,slidesToScroll:2}},{breakpoint:480,settings:{slidesToShow:1,slidesToScroll:1}}]});function format_currency(value){return "$"+parseInt(value).toString().replace(/(\d)(?=(\d{3})+$)/g,"$1.")}(function($){$.get=function(key){key=key.replace(/[\[]/,'\\[');key=key.replace(/[\]]/,'\\]');var pattern="[\\?&]"+key+"=([^&#]*)";var regex=new RegExp(pattern);var url=unescape(window.location.href);var results=regex.exec(url);if(results===null){return null}else{return results[1]}}})(jQuery);$(document).ready(function(){$(window).scroll(function(){if($(this).scrollTop()>120)$('.to-top').fadeIn();else $('.to-top').fadeOut()});$(".navbar a, footer a[href='#myPage']").on('click',function(event){if(this.hash!==""){event.preventDefault();var hash=this.hash;$('html, body').animate({scrollTop:$(hash).offset().top},900,function(){window.location.hash=hash})}});var altoHeader=$("#navbar-principal").height();$(".container-fixed-top").css("padding-bottom",altoHeader+"px");if(screen.width<991)
{$('#buttonsearch').click(function(){$('#formsearch').slideToggle("fast",function(){$('#buttonsearch').hide("fast")});$('#searchbox').focus()});$('#searchbox').blur(function(){$('#formsearch').hide("fast");$('#buttonsearch').css("display","block")})}
else{$('#formsearch').css("display","block");$('#buttonsearch').hide("fast")};setTimeout(function(){$(".alert").fadeOut(1500)},3000)});$.ajaxPrefilter(function(options,original_Options,jqXHR){options.async=!0})