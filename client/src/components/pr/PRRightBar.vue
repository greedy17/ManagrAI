<template>
  <div class="right-bar">
    <header>
      <h4>Select a Clip...</h4>
    </header>
    <footer>
      <!-- <button class="secondary-button">
        <img src="@/assets/images/sparkle.svg" height="14px" alt="" />
        Generate Clip Summary
      </button> -->
    </footer>
  </div>
</template>
<script>
import ChatTextBox from '../Chat/ChatTextBox.vue'
export default {
  name: 'PRRightBar',
  components: {
    ChatTextBox,
  },
  props: {},
  data() {
    return {
      selectedResource: 'Data',
      loading: false,
      message: '',
    }
  },
  watch: {},
  created() {},
  methods: {
    changeResource(resource) {
      this.selectedResource = resource
    },
    truncateTitle(title) {
      if (!title) {
        return ''
      }
      if (title.length <= 33) {
        return title
      }
      const titleSplit = title.split(' ')
      let newTitle = ''
      for (let i = 0; i < titleSplit.length; i++) {
        const word = titleSplit[i]
        newTitle += `${word} `
        if (newTitle.length >= 30) {
          const lastChar = newTitle[newTitle.length - 2]
          if (lastChar === ',' || lastChar === '.') {
            newTitle = newTitle.slice(0, newTitle.length - 2)
          } else {
            newTitle = newTitle.slice(0, newTitle.length - 1)
          }
          newTitle += '...'
          break
        }
      }
      return newTitle
      // return title.slice(0, 34) + '...'
    },
    setData() {
      this.loading = true
      setTimeout(() => {
        let articleCopy = { ...this.selectedArticle }
        // articleCopy.data = {
        //   impactScore: 8,
        //   impactScoreDetails: 'Talked positively about Tesla',
        //   keyMessages: `Tesla revolutionizes the automotive industry with sustainable innovation.`,
        //   summary: `The article discusses projections for U.S. new-vehicle sales in 2023 and lists the best-selling...`,
        //   topics: `Auto, Ford, Truck, Electric cars`,
        //   competitors: `Ford`,
        //   products: `Tesla Model X`,
        //   followUp: `No follow up is required`,
        // }
        this.$store.dispatch('updateSelectedArticle', articleCopy)
        this.loading = false
        // this.selectedArticle.data = {}
      }, 1500)
    },
  },
  computed: {
    selectedArticle() {
      return this.$store.state.selectedArticle
    },
    messages() {
      return this.$store.state.messages
    },
    userName() {
      return this.$store.state.user.firstName
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
.right-bar {
  background-color: $white;
  width: 100%;
  height: 100%;
  position: sticky;
  overflow-y: auto;
  padding-top: 74px;
}
.display-flex {
  display: flex;
}
.right-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0.5rem;
}
.gray-background {
  display: flex;
  align-items: center;
  background-color: $soft-gray;
  height: 5vh;
  // width: 16vw;
  width: 95%;
  border-radius: 8px;
}
.toggle-container {
  border: 1px solid $soft-gray;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  // width: 5vw;
  width: 30%;
  height: 3vh;
  border-radius: 8px;
  margin: 0 0.25rem;
  color: $light-gray-blue;
  p {
    margin: 0;
    font-size: 12px;
    // text-align: center;
  }
}
.active {
  background-color: $white;
  border-radius: 8px;
  color: $dark-black-blue;
}
.button-img {
  height: 14px;
}
.margin-right {
  margin-right: 0.5rem;
}
.right-side {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
.data-title {
  font-size: 14px;
  color: $light-gray-blue;
  margin-bottom: 0.25rem;
}
.data-detail {
  font-size: 13px;
  // color: $light-gray-blue;
  margin-top: 0.25rem;
  margin-left: 0.25rem;
  min-height: 1.5rem;
}
.data-container {
  width: 90%;
  margin-top: 1rem;
}
.data-content {
  height: 65vh;
  // border: 1px solid red;
  overflow-y: auto;
}
.add-edit-button {
  @include gray-text-button();
  padding-bottom: 0.5rem;
  padding-top: 0.5rem;
  position: relative;
  bottom: 0rem;
}
.chat-container {
  width: 90%;
  height: 70vh;
  overflow-y: auto;
}

header {
  position: sticky;
  top: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
  height: 50px;
  background-color: white;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;

  h4 {
    font-size: 13px;
    margin: 0;
  }
}

footer {
  position: absolute;
  left: 150px;
  bottom: 1rem;
}

.secondary-button {
  @include dark-blue-button();
  border: 1px solid $dark-black-blue;
  color: $dark-black-blue;
  background-color: white;
  padding: 10px 12px;
  img {
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}
.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
  margin: 0;
}
.message-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin: 0;
  width: 100%;
  padding: 0 1.5rem;

  p {
    padding: 0;
    margin: 0;
  }

  &:hover {
    background-color: $off-white !important;
  }
}

.message-container:first-of-type {
  padding-top: 0.5rem;
}
.margin-top {
  // margin-top: 4rem;
  // height: 96%;
  // overflow-y: auto;
}
.container-padding {
  border-radius: 6px;
  padding: 0.5rem;
}

.ai-text-container {
  overflow: scroll;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 0 0.75rem;
  line-height: 1.75;
  position: relative;

  &:hover {
    background-color: $off-white !important;
  }
}

.text-container {
  overflow: scroll;
  padding: 0.25rem;
  margin: 0;
  line-height: 1.75;
}

.images {
  padding: 0;
  margin: 0 0.5rem 0 0;
}

.bottom {
  position: sticky;
  bottom: 0;
  left: 0;
}

.bottom-right {
  position: absolute;
  bottom: 0;
  right: 0;
}

.avatar {
  background-color: $purple;
  color: white;
  width: 22px;
  height: 22px;
  margin-right: 0.2rem;
  margin-top: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-family: $base-font-family;
  background-color: white;

  h4,
  p {
    margin: 0;
    padding: 0.5rem;
    width: fit-content;
    // outline: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    // background-color: white;
    font-size: 12px;
    letter-spacing: 0.4px;

    span {
      color: $light-gray-blue;
    }
  }
}

@media (max-width: 768px) {
  .chat-container {
    font-size: 14px;
  }
}

.green-filter {
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
}
.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
  animation: shimmer 2s;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

.invert {
  filter: invert(95%);
}

.green {
  background-color: $dark-green !important;
  color: white !important;
  border: 1px solid $dark-green !important;
}

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

// .dot {
//   width: 4px;
//   height: 4px;
//   margin: 0 5px;
//   background: rgb(97, 96, 96);
//   border-radius: 50%;
//   animation: bounce 1.2s infinite ease-in-out;
// }

// .dot:nth-child(2) {
//   animation-delay: -0.4s;
// }

// .dot:nth-child(3) {
//   animation-delay: -0.2s;
// }

.col-start {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.generate-container {
  padding: 0 1rem 0.5rem 4.5rem;
  background-color: white;
  width: 100%;
}

.generate-button {
  @include chat-button();
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.5rem;
  img {
    margin-right: 0.5rem;
  }
}

.content-button {
  @include chat-button();
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 0.5rem;
  svg {
    margin-right: 0.5rem;
  }
}

.small-button {
  @include chat-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-radius: 5px;
  font-size: 12px;
  padding: 0.35rem;
  margin-left: 1rem;
  font-weight: normal;

  img {
    margin: 0;
    margin-right: 0.5rem;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.go-back {
  position: absolute;
  right: 0.5rem;
  top: -1.75rem;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.back {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }

  img {
    transform: rotate(180deg);
  }
}

.pointer {
  cursor: pointer;
}
// @keyframes typing {
//   from {
//     width: 0;
//   }
//   to {
//     width: 100%;
//   }
// }

// @keyframes blinking {
//   0% {
//     border-right-color: transparent;
//   }
//   50% {
//     border-right-color: rgb(66, 65, 65);
//   }
//   100% {
//     border-right-color: transparent;
//   }
// }

// .typed {
//   overflow: hidden;
//   white-space: nowrap;
//   width: 0;
//   animation: typing 1.5s steps(30, end) forwards, blinking 1s infinite;
//   border-right: 1px solid;
// }
.chat-button-container {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
}
.chat-border {
  background-color: $silver;
  padding: 0.25rem;
  border-radius: 4px;
}
.input-container {
  background-color: $white;
  padding: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 0 3px $very-light-gray;
  input {
    border: none;
    outline: none;
    width: 90%;
  }
}
.chat-window {
  min-height: 63vh;
}
.gray {
  color: rgb(82, 80, 80);
}
</style>