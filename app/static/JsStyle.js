      $(document).on('change', '.input-default-js', (e) => {

        const $this = $(e.target),
          $label = $this.next('label'),
          $files = $this[0].files;
        let fileName = '';

        if ($files && $files.length > 1)
          fileName = ($this.attr('data-multiple-target') || '').replace('{count}', $files.length);
        else if (e.target.value)
          fileName = e.target.value.split('\\').pop();

        if (fileName) {
          $label.find('.span-choose-file').html(fileName);
        } else {
          $label.html($label.html());
        }

      });