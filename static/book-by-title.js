"use strict";

function initSearchByTitleFormHandler() {
    $('#search-by-title-form').on('submit', evt => {
        evt.preventDefault();
        $('#bklist').empty();

        const formData = {
            title: $('#title-field').val()
        };

        $.get('/search-by-title.json', formData, (results) => {
            // pointers from https://stackoverflow.com/questions/26691776/dynamically-create-checkboxes-from-ajax-response
            let resultsObj = [];
            $.each(results, function (key, value) {

                resultsObj.push(value);
                let li = $('<li><a href="/books/'+ value.book_id + '"><input type="checkbox" class="bookCheckbox" name="'+ value.title + '" value="' + value.book_id + '"/>' + '<label for="' + value.book_id + '"></label></a></li>');
                li.find('label').text(value.title + " by " + value.author);
                $('#bklist').append(li);
                
            });
            console.log(resultsObj);
            return resultsObj
        });

    });
}
// how to collect clicks/submit form
// sidebar with all currently top rated books?
// then collect all and route into recommendation process
initSearchByTitleFormHandler();