import React from 'react';
import ReactDOM from 'react-dom';
import './index.css'

class App extends React.Component {

//  constructor(props) {
//    super(props);
//    this.state = {
//      error: null,
//      isLoaded: false,
//      items: [],
//    };
//  }
//
//  componentDidMount() {
//    fetch("http://localhost:5000/test")
//      .then(res => res.json())
//      .then(
//        (result) => {
//          this.setState({
//            isLoaded: true,
//            items: result.items,
//          });
//        },
//        (error) => {
//          this.setState({
//            isLoaded: true,
//            error,
//          });
//        }
//      )
//  }

 constructor(props) {
    super(props);
    this.state = {value: '',
                  query_type: '',
                  movieDetails: []};

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChangeOption = this.handleChangeOption.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
    console.log(this.state);
  }

  handleChangeOption(event) {
    console.log("updating query type")
    console.log(event.target.value)
    this.setState({query_type: event.currentTarget.value});
  }

  handleSubmit(event) {
    this.setState({movieDetails:[]})
    event.preventDefault();
    console.log("making request")

    fetch("http://localhost:5000/getMovie", {
        method:"POST",
        cache: "no-cache",
        headers:{
            "content_type":"application/json",
        },
        body:JSON.stringify([this.state.value, this.state.query_type])
        }
    ).then(response => {
        return response.json()
    }).then(json => {
        this.setState({movieDetails: json})
    })
  }


  render() {
    // eslint-disable-next-line
    const {value, movieDetails} = this.state;
      return (
      <div>

        <form onSubmit={this.handleSubmit}>
            <label>
              Movie Name:
              <input type="text" name="movie_name" onChange={this.handleChange} value={this.state.value}/>

              <input type="radio" id="movie" name="query_type" value="movie"
                  checked={this.state.query_type=='movie'} onChange={this.handleChangeOption} />
              <label htmlFor="movie">Movie</label>
              <input type="radio" id="genre" name="query_type" value="genre"
                  checked={this.state.query_type=='genre'} onChange={this.handleChangeOption} />
              <label htmlFor="genre">Genre</label>
              <input type="radio" id="bacon" name="query_type" value="bacon"
                  checked={this.state.query_type=='bacon'} onChange={this.handleChangeOption} />
              <label htmlFor="bacon">Bacon</label>

              <button type="submit">search</button>
            </label>
        </form>

        <div hidden={this.state.query_type !== 'movie'}>
            <h1> Movie Details </h1>
            <ol>
              {movieDetails.map(item => (
                <li key={item.tconst}>
                  {item.primarytitle} ({item.startyear})
                  <ul>
                      <li key={item.startyear}>
                        {item.role}: {item.name}
                      </li>
                  </ul>
                </li>
              ))}
            </ol>
        </div>

        <div hidden={this.state.query_type !== 'genre'}>
            <h1> Top {this.state.value} Movies </h1>
            <ol>
              {movieDetails.map(item => (
                <li key={item.tconst}>
                  {item.primarytitle} ({item.startyear}) - Rating: {item.averagerating} (out of {item.numvotes} votes)
                </li>
              ))}
            </ol>
          </div>

        <div hidden={this.state.query_type !== 'bacon'}>
            <h1> Bacon number of: {this.state.value} </h1>
              {movieDetails.map(item => (
                <p key={item.baconnumber}>
                  {item.baconnumber}
                </p>
              ))}
          </div>

      </div>

      );
  }
}


ReactDOM.render(
  <App/>,
  document.getElementById('root')
);
