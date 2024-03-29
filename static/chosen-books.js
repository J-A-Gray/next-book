"use strict";

function initCollectBooksFormHandler() {
    $('#results-from-search').on('submit', evt => {
        evt.preventDefault();
        $('#books-for-recommendations').removeClass('hidden')

        // pointers from https://stackoverflow.com/questions/5450104/using-jquery-to-get-all-checked-checkboxes-with-a-certain-class-name/14262603
        let checkedBooks = [];
        $('.bookCheckbox:checkbox:checked').map(function () {
            checkedBooks.push($(this).val());
            console.log(checkedBooks);
        });
        console.log(checkedBooks);
        for (let book of checkedBooks) {
            console.log(book);
            $.get('/search-by-book-id.json', {"book_id" : book}, (results) => {
                console.log(results);
                console.log(results.title);
                let set = $('<li><fieldset><a href="/books/'+ results.book_id + '"><legend>Placeholder for title</legend></a><p><input type="radio" name="'+ results.book_id + '" id="'+ results.book_id + '" value=5 checked><label for="loved">Loved it</label></p><p><input type="radio"  name="'+ results.book_id + '" id="'+ results.book_id + '" value=1><label for="hated">Hated it</label></p></fieldset></li>');
                set.find('legend').text(results.title + " by " + results.author);
                $('#chosenbklist').append(set);
        $($('#search-results').addClass('hidden'))


    });
}
});
}

initCollectBooksFormHandler();