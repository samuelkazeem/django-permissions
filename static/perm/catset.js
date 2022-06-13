window.onload = function(){
    // change buttons on pageload if form is being edited or reloaded
    changeButton();
}


function changeButton(argument) {
    // hide add buttons on all rows but last
    var conditionRow = $('.form-row:not(:last)');
    conditionRow.find('.btn.add-form-row').hide();
}


function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}


function cloneMore(selector, prefix) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    newElement.find(":input").not(':button').not(':submit').not(':reset').each(function() {
    	var name = $(this).attr('name');
    	var name_2 = name.replace('-' + (total-1) + '-', '-' + total + '-');
        var id = 'id_' + name_2;
        
    	$(this).attr({'name': name_2, 'id': id}).val('');
    });

    newElement.find('label').each(function() {
        var forValue = $(this).attr('for');
        if (forValue) {
          forValue = forValue.replace('-' + (total-1) + '-', '-' + total + '-');
          $(this).attr({'for': forValue});
        }
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);

    // alter buttons
    changeButton();

    return false;
}


function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
		//get div being removed
	    var div = btn.closest('.form-row');
        div.remove();
        var forms = $('.form-row');

        // make sure last div always has its add button showing
        $('div.form-row:last').find('.btn.add-form-row').show()
        
        //alter total forms length
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        
        // alter initial forms count
        var init_form = $('#id_' + prefix + '-INITIAL_FORMS')
        init_form.val(init_form.val()-1);

        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }

    return false;
}

$(document).on('click', '.add-form-row', function(e){
    e.preventDefault();
    cloneMore('div.form-row:last', 'form');
    return false;
});

$(document).on('click', '.remove-form-row', function(e){
    e.preventDefault();
    deleteForm('form', $(this));
    return false;
});