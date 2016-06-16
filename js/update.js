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

  var filename = '';
  if (date != 'null') {
    filename = 'data/' + date.replace('/','') + '.json';
  } else {
    filename = 'data/now.json';
  }

  var template_row = Mustache.compile(" \
    <tr> \
      <td>{{ idx }}</td> \
      <td><a href=\"{{ url }}\" class=\" hnlink \" target=\"_blank\">{{ title }} <small>({{ domain }})</small></a></td> \
      <td><a href=\"http://news.ycombinator.com/user?id={{ user }}\" class=\" hnlink \" target=\"_blank\">{{ user }}</a></td> \
      <td><p class=\"text-center\"><a href=\"http://news.ycombinator.com/item?id={{ thread_id }}\" class=\" hnlink \" target=\"_blank\">{{ num_comments }}</a></p></td> \
      <td><p class=\"text-center\">{{ points }}</p></td> \
      <td><small<time class=\"timeago\" datetime=\" {{ iso_string }}\">{{ timeago_string }}</time></small></td> \
    </tr>");

  var all_data = {};
  $(".imgloader").show();
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
      all_data_list.push(row);
    });

    $(".imgloader").hide();
    $.each(all_data_list.sort(compare_by_points).reverse(), function(idx,row) {
      var d = new Date(0);
      d.setUTCSeconds(row.posted_time);
      var cur = new Date();
      var timeDiff = Math.abs(cur.getTime() - d.getTime());
      var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
      row.idx = idx + 1;
      row.timeago_string = jQuery.timeago(d);
      row.iso_string = d.toISOString();
      var output = template_row(row);
      if (diffDays <= 1) {
          $('#data-table').append(output);
      }
    });
  })
  .error(function(){
    $('body .table:first').html('Could not load data at ' + filename);
  });
});