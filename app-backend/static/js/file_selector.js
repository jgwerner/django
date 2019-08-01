(function() {
    document.querySelectorAll('.directory').forEach(function(item) {
      item.onclick = function (e) {
        var fileList = e.target.closest('.project').querySelector('ul'),
            arrowDown = e.target.parentElement.querySelector('.arrow-down'),
            arrowRight = e.target.parentElement.querySelector('.arrow-right');
        if (fileList.style.display === "none") {
          fileList.style.display = "block";
          arrowDown.style.display = "inline";
          arrowRight.style.display = "none";
        } else {
          fileList.style.display = "none";
          arrowDown.style.display = "none";
          arrowRight.style.display = "inline";
        }
      }
    });
    var form = document.getElementById("fileForm");
    form.onsubmit = submit;
    function submit(e) {
      e.preventDefault();
      var input = document.querySelector('input[name="content_items"]:checked');
      var path = input.getAttribute("data-path");
      var project = input.getAttribute("data-project");
      var url = `${window.location.origin}/{{ version }}/{{ namespace }}/projects/${project}/assignments/`
      fetch(url, {
          method: 'post',
          body: JSON.stringify({
              external_id: '{{ assignment_id }}',
              path: path,
              lms_instance: '{{ canvas_instance_id }}',
              oauth_app: '{{ oauth_app }}',
              teacher_project: project,
              course_id: '{{ course_id }}',
          }),
          headers: {
              'Content-Type': 'application/json',
              'Authorization': 'JWT {{ token }}',
          },
      }).then(() => form.submit()).catch(err => alert(`There was an error selecting assignment:\n ${err}`));
    }
  }());