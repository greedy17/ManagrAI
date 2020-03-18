<template>
  <div class="call-action">
    <div class="call-action-left-pane">
      <div class="contacts-container">
        <div class="contact">
          <img class="contact-img" src="/sara-smith.png" />
          <span class="contact-name">Sara Smith</span>
          <div class="contact-phone-number-container">
            <img class="telephone-icon" src="/telephone.svg" />
            <span class="contact-phone-number">555-555-5555</span>
          </div>
        </div>
        <div class="contact">
          <img class="contact-img" src="/jake-murray.png" />
          <span class="contact-name">Jake Murray</span>
          <div class="contact-phone-number-container">
            <img class="telephone-icon" src="/telephone.svg" />
            <span class="contact-phone-number">555-555-5555</span>
          </div>
        </div>
      </div>
      <div class="details-container">
        <input placeholder="Title" />
        <input :placeholder="date" />
      </div>
    </div>
    <div class="call-action-right-pane">
      <div class="text-area-container">
        <textarea placeholder="Detail" />
      </div>
      <div class="save-button-container">
        <span class="save-button">Save</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallAction',
  computed: {
    date() {
      let today = new Date()
      let dd = String(today.getDate()).padStart(2, '0')
      let mm = String(today.getMonth() + 1).padStart(2, '0') //January is 0!
      let yyyy = today.getFullYear()
      return mm + '/' + dd + '/' + yyyy
    },
  },
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

.call-action {
  width: 100%;
  display: flex;
  flex-flow: row;
}

/* left pane below */
.call-action-left-pane {
  width: 40%;
  padding-right: 3%;
  display: flex;
  flex-flow: column;
}

.contacts-container {
  display: flex;
  flex-flow: column;
}

.contact {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 2%;
}

.contact-img {
  height: 24px;
  width: 24px;
  border-radius: 50%;
}

.contact-name {
  margin-left: auto;
  width: 25%;
  font-family: Lato;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;
}

.contact-phone-number-container {
  width: 50%;
  height: 24px;
  padding: 2px;
  margin-left: auto;
  background-color: #efeff5;
  border-radius: 5px;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.telephone-icon {
  height: 16px;
  width: 16px;
  margin-left: 5px;
}

.contact-phone-number {
  margin-left: 5px;
  font-family: Lato;
  font-size: 11px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;
}

.details-container {
  margin-top: 3%;
  display: flex;
  flex-flow: column;
}

input {
  height: 40px;
  margin: 5px 0;
  border-radius: 4px;
  background-color: #fafafa;
  border: none;
  box-sizing: border-box;
  padding: 3%;

  &:focus {
    box-shadow: 0 0 10px rgba($color: #199e54, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: 'Lato', sans-serif;
    font-size: 14px;
    font-weight: normal;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: #444444;
  }
}

/* right-pane below */
.call-action-right-pane {
  flex-grow: 1;
  display: flex;
  flex-flow: column;
}

.text-area-container {
  height: 95%;
  display: flex;
  align-items: top;
  justify-content: center;
}

textarea {
  resize: none;
  height: 94%;
  width: 100%;
  box-sizing: border-box;
  padding: 3%;
  border-radius: 4px;
  border: none;
  background-color: #fafafa;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #444444;

  &:focus {
    box-shadow: 0 0 10px rgba($color: #199e54, $alpha: 0.5);
    outline: none;
    background-color: #ffffff;
  }

  &::placeholder {
    opacity: 0.5;
    font-family: 'Lato', sans-serif;
    font-size: 14px;
    font-weight: normal;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: #444444;
  }
}

.save-button-container {
  display: flex;
  flex-flow: row;
}

.save-button {
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 15px;
  border-radius: 5px;
  background-color: #199e54;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #ffffff;

  &:hover {
    cursor: pointer;
  }
}
</style>
