/**
 * Created by demarq on 15.09.18.
 */

function removeButton(){
    var form_input = document.getElementById('form_input');
    var config = document.forms['form']['settings'].value;
    if (!config){
        alert('Выберите конфигурацию');
        return false;
    }
    else {
        form_input.parentNode.removeChild(form_input);
        var form = document.getElementById('form');
        form.submit();
    }
}