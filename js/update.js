$(document).ready(function(){
  function compare_by_points(a,b) {
    if (a.points < b.points)
      return -1;
    if (a.points > b.points)
      return 1;
    return 0;
  }

  function getURLParameter(name) {
    return decodeURI(
        (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]
    );
  }

  var date = getURLParameter('date');
  // console.log('Date: ' + date);

  var filename = '';
  if (date != 'null') {
    filename = 'data/' + date.replace('/','') + '.json';
  } else {
    filename = 'data/now.json';
  }

  var template_row = Mustache.compile(" \
    <tr> \
      <td>{{ idx }}</td> \
      <td><a href=\"{{ url }}\" target=\"_blank\">{{ title }} <small>({{ domain }})</small></a></td> \
      <td><a href=\"http://news.ycombinator.com/user?id={{ user }}\" target=\"_blank\">{{ user }}</a></td> \
      <td><a href=\"http://news.ycombinator.com/item?id={{ thread_id }}\" target=\"_blank\">{{ num_comments }}</a></td> \
      <td>{{ points }}</td> \
      <td>{{ posted_time_string }}</td> \
    </tr>");

  var all_data = {};

  $.getJSON(filename,function(json){
    // console.log(json);

    $.each(json, function(idx, row) {
      if (row.thread_id) {
        // If this is a link to an HN page
        if (row.url.indexOf('http') == -1) {
          row.url = 'https://news.ycombinator.com/' + row.url;
        }

        // console.log(row);

        if(row.thread_id in all_data) {
          row.points = parseInt(row.points,10);
          row.num_comments = parseInt(row.num_comments,10);
          if (row.points > all_data[row.thread_id].points) {
            all_data[row.thread_id] = row;
          }
          // Get the earliest date
          if (row.posted_time < all_data[row.thread_id].posted_time) {
            all_data[row.thread_id].posted_time = row.posted_time;
          }
        } else {
          all_data[row.thread_id] = row;
        }
      }
    });

    var all_data_list = [];
    $.each(all_data, function(thread_id,row) {
      // console.log(row);
      all_data_list.push(row);
    });

    $.each(all_data_list.sort(compare_by_points).reverse(), function(idx,row) {
      var d = new Date(0);
      d.setUTCSeconds(row.posted_time);
      row.idx = idx + 1;
      row.posted_time_string = d.toLocaleString();
      var output = template_row(row);
      $('#data-table').append(output);
    });
  })
  .error(function(){
    $('body .span12:first').html('Could not load data at ' + filename);
  });
});