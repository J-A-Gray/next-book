
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
        const bookData = this.state.attributes
        if (this.state.isLoaded) {
            return (
                <div>
                    <img src={this.state.attributes.cover_img} />
                    <h1>{this.state.attributes.title}</h1>
                    <h2>{this.state.attributes.author}</h2>
                    <p>{this.state.attributes.summary}</p>
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