var edit_doc;

$(document).ready(function() {
    edit_doc = $('#edit');
    designMode('on');
    
    $('#bold').click(function(){
        editCommand('bold');
    });
    $('#italic').click(function(){
        editCommand('italic');
    });
    $('#line').click(function(){
        editCommand('underline');
    });
    $('#strike').click(function(){
        editCommand('strikethrough');
    });
    $('#size').click(function(){
        editCommand('Bold');
    });
    $('#heading').click(function(){
        editCommand('Bold');
    });
    $('#nlist').click(function(){
        editCommand('insertorderedlist');
    });
    $('#blist').click(function(){
        editCommand('insertunorderedlist');
    });
    $('#iindent').click(function(){
        editCommand('indent');
    });
    $('#dindent').click(function(){
        editCommand('outdent');
    });
    $('#alignl').click(function(){
        editCommand('justifyleft');
    });
    $('#alignc').click(function(){
        editCommand('justifycenter');
    });
    $('#alignr').click(function(){
        editCommand('justifyright');
    });

});

function designMode(mode){
    edit_doc[0].contentDocument.designMode=mode;
}

function editCommand(aName, aArg){
    edit_doc[0].contentDocument.execCommand(aName, false, aArg);
    edit_doc[0].contentWindow.focus();
}
