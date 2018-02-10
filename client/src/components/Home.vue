<template>
  <form>
    <fieldset>
      <label for="nameField">Model Name</label>
      <input type="text" placeholder="Eg: Life Insurance" id="nameField">
      <br>
      <label for="commentField">Description</label>
      <textarea placeholder="Describe this Risk Type" id="commentField"></textarea>
      <div v-for="n in range" :key="n">
        <label for="commentField">Field <span v-bind="n"></span></label>
        <input type='text' id='confirmField' placeholder="Field Name">

        <div class="float-left" v-for="(attributes, field, index) in dataTypes" :key="index">
          <input type='checkbox' name='fieldType' id='confirmField'>
          <label class='label-inline' for='confirmField'>
            {{field}}, Attributes:  {{attributes}}
          </label>
        </div>
        <br>
      </div>
      <div class="float-right" v-on:click="addForm()"><a >Add model field</a></div>
      <div class="float-left">
        <input class="button-primary" type="submit" value="Create">
      </div>
    </fieldset>
  </form>
</template>

<script type="text/javascript">
import axios from 'axios';

export default {
  data() {
    return {
      dataTypes: {},
      range: 0,
    };
  },
  methods: {
    getDataType() {
      const path = '/' + (process.env.FLASK_ENV ? process.env.FLASK_ENV : '') + '_api/types';
      axios.get(path)
        .then((response) => {
          this.dataTypes = response.data;
          console.log(this.dataTypes);
        })
        .catch((error) => {
          console.log(error);
          this.dataTypes = {};
        });
    },
    addForm() {
      this.range += 1;
    },
  },
  created() {
    this.getDataType();
  },
};

</script>
