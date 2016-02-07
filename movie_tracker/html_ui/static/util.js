function renderMovies(movies, enable_selection) {
    enable_selection = (typeof enable_selection != 'undefined') ? enable_selection : false;

    selection_header = (enable_selection == false)? "" : "<th> select </th> ";
    var htmlContent = "<tr> " + selection_header + "<th> Name </th> <th> size </th> <th> file </th> <th> date_added </th> </tr> \n";
    for(var i=0; i<movies.length; ++i) {
        selection = (enable_selection == false)? "" : "<td> <input type='checkbox' value='"+movies[i].movie_id+
                              "' class='selected_movie'> </input> </td>";
        htmlContent += "<tr>"+
                        selection +
                        " <td> <a href=\"/movie/" + movies[i].movie_id + "\"> "+ movies[i].movie_name + "</a> </td>" +
                        " <td align=\"right\"> " + movies[i].movie_file_size_mb.toFixed(2) + "</td> "+
                        " <td> " + movies[i].movie_file + "</td> " +
                        " <td> " + movies[i].date_added + "</td> " +
                        " </tr> \n";
    }
    $("#movie_details").html(htmlContent);
    $("#movie_details th").click(getSorterByTableId("movie_details"));
}

function getSorterByTableId(tableId){
            return function() {
                var column_idx = $("#"+tableId+" th").index($(this));
                var new_rows = [];
                new_rows.push( $("#"+tableId+" tr:eq(0)"));
                var rows = $("#"+tableId+" tr:gt(0)");
                this.ascending = !this.ascending;
                rows.sort(function (a, b) {
                    var a_val = $(a).children("td").eq(column_idx).text();
                    var b_val = $(b).children("td").eq(column_idx).text();

                    a_val = a_val == parseFloat(a_val)? parseFloat(a_val): a_val; // Handle numeric values
                    b_val = b_val == parseFloat(b_val)? parseFloat(b_val): b_val;

                    return (a_val<b_val)?-1:(a_val>b_val?1:0);
                });
                if(!this.ascending) rows = rows.get().reverse();
                for(var i=0; i<rows.length; ++i) { new_rows.push(rows[i]);}
                $("#"+tableId).append(new_rows);
            }
        }

function getSelectedMovieIds() {
var selectedElements = $(".selected_movie:checked");
            var selectMovieIds = [];
            for(var i=0; i<selectedElements.length; ++i) {
                selectMovieIds[i] = selectedElements[i].value;
            }
            return selectMovieIds;
}