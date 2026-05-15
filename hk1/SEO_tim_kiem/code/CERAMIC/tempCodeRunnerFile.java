<!DOCTYPE html>

<html>

  <body>

    <button onclick="changeColor()">Change Color</button>

    <script>

      function changeColor() {

        const colors = ['pink', 'lightblue', 'lightgreen', 'lavender'];

        const randomIndex = Math.floor(Math.random() * colors.length);

        document.body.style.backgroundColor = colors[randomIndex];

      }

    </script>

  </body>

</html>