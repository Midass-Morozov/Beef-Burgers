document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    document.querySelectorAll('.alert').forEach(function (el) {
      if (window.bootstrap) {
        const a = bootstrap.Alert.getOrCreateInstance(el);
        a.close();
      }
    });
  }, 4000);
});