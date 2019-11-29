// custom javascript

$( document ).ready(function() {
  console.log('Sanity Check!');
  $('input[type=checkbox]').each(function() {
      toggle_questions($(this)[0]);
  });
});

function toggle_questions(question) {
    name = question.name;
    if(question.checked) {
        $("#"+name+"_trueform").show();
        $("#"+name+"_falseform").hide();
    } else {
        $("#"+name+"_falseform").show();
        $("#"+name+"_trueform").hide();
    };
}
