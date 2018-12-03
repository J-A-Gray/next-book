"use strict";

function initSearchByAuthorFormHandler() {
    $('#search-by-author-form').on('submit', evt => {
        evt.preventDefault();
        $('#search-results').removeClass('hidden')
        $('#bklist').empty();

        const formData = {
            author: $('#author-field').val()
        };

        $.get('/search-by-author.json', formData, (results) => {
            // pointers from https://stackoverflow.com/questions/26691776/dynamically-create-checkboxes-from-ajax-response
            $.each(results, function (key, value) {
                let li = $('<li><a href="/books/'+ value.book_id + '"><input type="checkbox" class="bookCheckbox" name="'+ value.title + '" value="' + value.book_id + '"/>' + '<label for="' + value.book_id + '"></label></a></li>');
                li.find('label').text(value.title + " by " + value.author);
                $('#bklist').append(li);
            });
        });
    });
}

initSearchByAuthorFormHandler();