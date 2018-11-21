function initSearchByAuthorFormHandler() {
    $('#search-by-author-form').on('submit', evt => {
        evt.preventDefault();

        const formData = {
            author: $('#author-field').val()
        };

        $.get('/search-by-author.json', formData, (results) => {
            // pointers from https://stackoverflow.com/questions/26691776/dynamically-create-checkboxes-from-ajax-response
            $.each(results, function (key, value) {
                let li = $('<li><input type="checkbox" class="bookCheckbox" name="'+ value.title + '" value="' + value.book_id + '"/>' + '<label for="' + value.book_id + '"></label></li>');
                li.find('label').text(value.title);
                $('#bklist').append(li);
            });
        });
    });
}

initSearchByAuthorFormHandler();