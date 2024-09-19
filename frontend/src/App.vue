<template>
  <div>
    <h1>Search for Concerts by City</h1>
    <form @submit.prevent="searchConcerts">
      <label for="city">Enter City Name:</label>
      <input type="text" id="city" v-model="city" />
      <input type="submit" value="Search" />
    </form>

    <div v-if="concerts.length">
      <h2>Concert Results:</h2>
      <ul>
        <li v-for="(concert, index) in concerts" :key="index">{{ concert }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      city: '',     // User input for city
      concerts: []  // Concert results from the backend
    };
  },
  methods: {
    searchConcerts() {
      axios.post('/api/concerts', { city: this.city })
        .then(response => {
          this.concerts = response.data.concerts;
        })
        .catch(error => {
          console.error("There was an error!", error);
        });
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
