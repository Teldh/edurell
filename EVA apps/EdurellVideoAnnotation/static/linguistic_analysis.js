console.log(concept_map)
console.log(concepts)

let options = "<option value='ANY CONCEPT'>ANY CONCEPT</option>";
for(let i = 0; i < concepts.length; i++) {
    options += "<option value='" + concepts[i] + "'>" + concepts[i] + "</option>";
}
$('select[name="prerequisite_name"]').append(options)
$('select[name="target_name"]').append(options)



$("#find").click(function () {
    //erase the paper from previous results and re-populate it
    //$('#paper').html("");
    $('#results').empty();

    //let selectedSentence = $('#sent_id').val();
    let selectedPrereq = $('#prerequisite_name').val();
    let selectedTarget = $('#target_name').val();
    let selectedWeight = $('#edge_weight').val();

    let no_relations_matched = true;
    let counter = 0;

    for (let rel of concept_map) {
        console.log(selectedPrereq,selectedTarget,selectedWeight)
        if ((selectedPrereq === "ANY CONCEPT" || rel['prerequisite'] === selectedPrereq) &&
            (selectedTarget === "ANY CONCEPT" || rel['target'] === selectedTarget) &&
            (selectedWeight === "ANY WEIGHT" || rel['weight'] === selectedWeight) ) /*&&
            (selectedSentence === "ANY SENTENCE" || rel['sent'].toString() === selectedSentence))*/ {

            if(no_relations_matched)
                no_relations_matched = false;

            counter += 1;

            let currSent = rel["sentence"];

            // coloro prerequisito in giallo e target in verde
            // var sentence = color_word_in_sentence(rel['prerequisite'], currSent, "#ff6666");
            // sentence = color_word_in_sentence(rel['target'], sentence, "lightblue");

            console.log(counter, counter % 2)

            let background = ""
            if(counter % 2 == 0)
                background = 'style="background-color: white"'


            $("#results").append('' +
                '<div '+ background +'>' +
                    '<div class="container" style="padding:10px">'+
                        '<p class="titleLower"> ' +rel["prerequisite"] +'<i style="font-size:18px" class="fas"> &#xf061; </i>' + rel["target"] +
                        '</p>'+ rel["time"]+
                        '<br>'+ rel["sentence"]+
                    '</div>'+
                    '<br>'+
                '</div>'
                // '<div> ' +
                // '     <span style="font-weight: bold;">Sentence:</span> ' + "(... id)" +
                // '   <table class="table table-bordered">'+
                // '       <tr><td>' + currSent+
                // //'           ' + sentence[0] +'<span>'+ rel['prerequisite'] +'</span>'+ sentence[1] +'</td>' +
                // '       </td></tr>'+
                // '   </table>' +
                // '   <div  style="float:right; margin-top: -15px;">' +
                // '       <button type="button" class="btn btn-primary btn-sm result_text"' +
                // /*' data-rel_id="' + insertedRelations.indexOf(rel) + '"' +
                // ' data-sent_id="' + rel['sent'] + '"' +*/
                // ' data-prereq="' + rel['prerequisite'] + '"' +
                // ' data-target="' + rel['target'] + '"' +
                // ' data-weight="' + rel['weight'] + '"' +
                // '">Show context</button>'+
                // '   </div>' +
                // '</div><br><br>'
            );

        }
    }

    if(no_relations_matched)
        $("#results").append('<div class="container"><span style="font-weight: bold;">No relations matched your critera</span></div> ');

    $('html, body').animate({
        scrollTop: $("#results").offset().top
    }, 1000);
});