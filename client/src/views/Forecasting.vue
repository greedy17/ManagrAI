<template>
  <div class="pipelines">
    <div class="pipelines__center">
      <div>
        <div class="spacer"></div>
        <span style="color: #45a16f">Introducing Forecasting</span>
        <h1>Coming Soon.</h1>
        <p style="margin-top: -1rem">
          Email us at mike@mymanagr.com if you have any feedback or questions.
        </p>
      </div>

      <div class="preview-border">
        <img
          src="@/assets/images/forecasting.png"
          style="height: 70vh; width: 50vw; margin-left: 0.5rem"
          alt=""
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Forecasting',
  data() {
    return {}
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/buttons';

.pipelines {
  margin-top: 3rem;
  color: $base-gray;

  &__preview {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    margin: 1rem 3rem;
    z-index: 2;
  }
  &__center {
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
  }
}

.preview-border {
  box-shadow: 4px 5px 9px $very-light-gray;
  background-color: white;
  margin-top: 2rem;
  border-radius: 0.5rem;
  width: 51vw;
}
.spacer {
  height: 20vh;
}
p {
  font-size: 14px;
}
h1 {
  margin-top: -1px;
  margin-left: -0.1rem;
  font-size: 38px;
}
</style>