class Books extends React.Component {
    constructor() {
    super()

    this.state = {
            isLoaded: false,
            bookList: []
        }

    }

    componetDidMount() {

        $.get('/api/popular', result => {
            this.setState({bookList: result, isLoaded: true})
        })

    }

    render() {

        if (this.state.isLoaded) {
            return(
                this.state.bookList.map((book, key) =>
                    <Book book={book} key={book.book_id} />
                )
            )

        } else {

            this.componetDidMount()
            return (
                <div>
                    <p>Loading...</p>
                </div>)

        }
    }

}

class Book extends React.Component {
    constructor() {
    super()

    this.state = {
            isLoaded: false,
            attributes: []
        }

    }

    componetDidMount() {
        const path = '/api/books/'
        let api = (path).concat(this.props.book.book_id)

        $.get(api, result => {
            this.setState({attributes: result, isLoaded: true})
        })
  
    }

    render () {
        if (this.state.isLoaded) {

            return (
                (
                    <div>
                        {this.state.attributes.cover_img && (
                            <div>
                                <img src={this.state.attributes.cover_img}></img>
                            </div>)}
                    
                        <div>
                            <a href = {this.state.attributes.titleLink}>
                            <h1>{this.props.book.title}</h1>
                            </a>
                        </div>
                        
                        <div id="book-author">
                            <a href = {this.state.attributes.authorLink}>
                                <h2>{this.props.book.author}</h2>
                             </a>
                        </div>
    
                        <br />

                        {this.state.attributes.summary && 
                            (<p className='summary'>{this.state.attributes.summary}</p>)}
                            
                        {this.state.attributes.previewURL && 
                            (<a href={this.state.attributes.previewURL}>Preview Me!</a>)}

                        {this.state.attributes.excerpts && 
                            (<blockquote className="first-line">{this.state.attributes.excerpts}</blockquote>)}
                        
                        {this.state.attributes.avgRating && 
                            (<p>Average Rating: {this.state.attributes.avgRating}</p>)}
           
                    </div>))
    } else {

            this.componetDidMount()
            return (
                <div>
                    <p>Loading...</p>
                </div>)

        }
    }
}

ReactDOM.render(<div><Books /></div>, document.getElementById('root'))