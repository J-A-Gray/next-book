class Book extends React.Component {
    constructor() {
    super()

    this.state = {
            isLoaded: false,
            attributes: []
        }

    }

    componetDidMount() {
        const path = window.location.pathname
        let api = (path).concat("/info.json")

        $.get(api, result => {
            this.setState({attributes: result, isLoaded: true})
        })
  
    }

    render() {

        if (this.state.isLoaded) {
            console.log(this.state.attributes)
            return (
                <div>
                    <img src={this.state.attributes.cover_img} />

                    <div>
                        <a href = {this.state.attributes.titleLink}>
                            <h1>{this.state.attributes.title}</h1>
                        </a>
                    </div>

                    <div id="book-author">
                        <a href = {this.state.attributes.authorLink}>
                        <h2>{this.state.attributes.author}</h2>
                        </a>
                    </div>

                    {this.state.attributes.summary && 
                            (<p className='summary'>{this.state.attributes.summary}</p>)}

                    {this.state.attributes.previewURL && 
                            (<a href={this.state.attributes.previewURL}>Preview Me!</a>)}

                    {this.state.attributes.excerpts && 
                        (<blockquote className="first-line">{this.state.attributes.excerpts}</blockquote>)}
                        
                    {this.state.attributes.avgRating && 
                        (<p>Average Rating: {this.state.attributes.avgRating}</p>)}
                      
                </div>)
        } else {

            this.componetDidMount()
            return (
                <div>
                    <p>Loading...</p>
                </div>)

        }
    }

}

ReactDOM.render(<div><Book /></div>, document.getElementById('root'))