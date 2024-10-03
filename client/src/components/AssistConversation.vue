<template>
  <div>
    <!-- v-if="currentChat.view === 'news'" -->
    <div>
      <div
        v-if="userResponse && currentChat.view !== 'write' && currentChat.view !== 'report'"
        class="space-between"
      >
        <div></div>
        <div class="chat-bubble row">
          <img src="@/assets/images/profile.svg" height="12px" alt="" />
          <p>{{ userResponse }}</p>
        </div>
      </div>

      <div
        v-if="userResponse && currentChat.details && currentChat.view !== 'write'"
        class="space-between"
      >
        <div class="chat-bubble row">
          <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
          <p v-typed="currentChat.responseText"></p>
        </div>

        <div></div>
      </div>

      <div v-if="secondResponse" class="space-between">
        <div></div>
        <div class="chat-bubble row">
          <img src="@/assets/images/profile.svg" height="12px" alt="" />
          <p>{{ secondResponse }}</p>
        </div>
      </div>

      <div
        v-if="secondResponse && currentChat.details && currentChat.view === 'write'"
        class="space-between"
      >
        <div class="big-chat-bubble">
          <div class="row">
            <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
            <p class="bold-text" v-typed="currentChat.responseText"></p>
          </div>
          <div class="bubble-body">
            <div class="relative">
              <div
                @click.stop="toggleSuggestions"
                class="drop-header-alt"
                style="background-color: #fafafa; box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.1)"
              >
                <p style="font-size: 15px !important" class="mobile-text-hide">Suggestions</p>
                <img
                  v-if="!showSuggestions"
                  src="@/assets/images/arrowDropUp.svg"
                  height="15px"
                  alt=""
                />
                <img
                  v-else
                  class="rotate-img"
                  src="@/assets/images/arrowDropUp.svg"
                  height="15px"
                  alt=""
                />
              </div>

              <div
                v-show="showSuggestions"
                v-outside-click="hideSuggestions"
                class="container-left-below"
              >
                <h3 style="padding-top: 0; padding-bottom: 0">Content suggestions</h3>
                <div>
                  <p
                    v-for="(suggestion, i) in suggestions"
                    :key="i"
                    @click="selectSuggestion(suggestion.value)"
                  >
                    {{ suggestion.name }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div></div>
      </div>

      <div v-if="thirdResponse" class="space-between">
        <div></div>
        <div class="chat-bubble row">
          <img src="@/assets/images/profile.svg" height="12px" alt="" />
          <p>{{ thirdResponse }}</p>
        </div>
      </div>

      <div v-if="(loading || summaryLoading) && currentChat.view !== 'write'" class="space-between">
        <div class="chat-bubble row">
          <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
          <p v-typed="searchText"></p>
          <img class="rotation" src="@/assets/images/loading.svg" height="14px" alt="" />
        </div>
        <div></div>
      </div>

      <div
        v-else-if="(loading || summaryLoading) && currentChat.view === 'write'"
        class="space-between"
      >
        <div class="chat-bubble row">
          <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
          <p v-typed="writeSearchText"></p>
          <img class="rotation" src="@/assets/images/loading.svg" height="14px" alt="" />
        </div>
        <div></div>
      </div>

      <div v-else-if="responseEmpty" class="space-between">
        <div class="space-between">
          <div class="chat-bubble row">
            <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
            <p v-typed="noResponseText"></p>
          </div>
          <!-- <div class="big-chat-bubble">
            <div class="row">
              <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
              <p v-typed="noResponseText"></p>
            </div>
            <div class="bubble-body">
              <p>Try one of these searches:</p>

              <div class="row">
                <div class="suggestion">
                  suggestion 1 <img src="@/assets/images/rightarrow.svg" height="12px" alt="" />
                </div>
                <div class="suggestion">
                  suggestion 2 <img src="@/assets/images/rightarrow.svg" height="12px" alt="" />
                </div>
                <div class="suggestion">
                  suggestion 3 <img src="@/assets/images/rightarrow.svg" height="12px" alt="" />
                </div>
              </div>
            </div>
          </div> -->

          <div></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssistConversation',
  data() {
    return {
      showSuggestions: false,
      searchText: 'Searching...',
      writeSearchText: 'Writing...',
      noResponseText: 'No results found. Try again',
      suggestions: [
        {
          name: `Craft a short media pitch for...`,
          value: `Craft a short media pitch for {BrandX}`,
        },
        {
          name: `Write a press release for...`,
          value: `Write a press release for {Brand}. Emphasize key statistics and link them to industry trends. Use an attention-grabbing headline, crucial details early on, and compelling quotes. Aim for an engaging narrative that appeals to journalists.
          `,
        },
        {
          name: `Draft a Linkedin post...`,
          value: `Draft a LinkedIn post about {Topic}`,
        },
      ],
    }
  },
  methods: {
    toggleSuggestions() {
      this.showSuggestions = true
    },
    hideSuggestions() {
      this.showSuggestions = false
    },
    selectSuggestion(val) {
      this.$emit('setChatSuggestion', val)
      this.showSuggestions = false
    },
  },
  props: {
    currentChat: {
      default: null,
    },
    userResponse: {
      default: null,
    },
    secondResponse: {
      default: null,
    },
    thirdResponse: {
      default: null,
    },
    loading: {
      default: false,
    },
    summaryLoading: {
      default: false,
    },
    responseEmpty: {
      default: false,
    },
  },
  directives: {
    typed: {
      bind(el, binding) {
        let text = binding.value
        let index = 0
        el.innerHTML = ''

        function type() {
          if (index < text.length) {
            el.innerHTML += text.charAt(index)
            index++
            setTimeout(type, 10)
          }
        }

        type()
      },
      //   update(el, binding) {

      //     let text = binding.value
      //     let index = 0
      //     el.innerHTML = ''

      //     function type() {
      //       if (index < text.length) {
      //         el.innerHTML += text.charAt(index)
      //         index++
      //         setTimeout(type, 50)
      //       }
      //     }

      //     type()
      //   },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.chat-bubble {
  width: fit-content;
  border-radius: 20px;
  padding: 12px 16px;
  margin: 12px 0;
  background-color: white;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);

  img {
    margin-right: 6px;
  }

  p {
    margin: 0;
  }
}

.big-chat-bubble {
  width: fit-content;
  border-radius: 20px;
  padding: 12px 16px;
  margin: 12px 0;
  background-color: white;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);

  img {
    margin-right: 6px;
  }

  p {
    margin: 0;
  }

  .bubble-body {
    padding-left: 20px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
  }
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotation {
  animation: rotation 2s infinite linear;
  margin-left: 4px;
}

.suggestion {
  font-size: 14px;
  width: 200px;
  padding: 10px 12px;
  border: 0.5px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  background-color: white;
  margin: 0 !important;
  cursor: pointer;
  transition: all 0.5s;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  p {
    margin: 0;
    font-family: $base-font-family;
    font-weight: 200;
  }
}

.soft-gray-bg {
  background-color: $soft-gray !important;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 1s forwards;
}

.bold-text {
  font-family: $base-font-family;
  font-size: 16px;
}

.drop-header-alt {
  padding: 8px 10px;
  width: fit-content;
  background-color: white;
  font-size: 14px !important;
  border-radius: 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;
  margin: 8px 0;

  @media only screen and (max-width: 600px) {
    font-size: 12px !important;
  }

  img {
    margin: 0 8px;
    filter: invert(40%);

    @media only screen and (max-width: 600px) {
      // display: none;
    }
  }

  small {
    font-size: 14px;
    margin-left: 4px !important;
    font-family: $base-font-family;
    max-width: 55px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  p,
  small {
    margin: 0;
    padding: 0;
  }

  &:hover {
    background-color: $soft-gray;
  }
}

.container-left-below {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  position: absolute;
  left: 0;
  bottom: 44px;
  height: 150px;
  width: 350px;
  padding: 0 0 16px 0;
  background-color: white;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  z-index: 9;
  //   overflow-y: scroll;

  //   &::-webkit-scrollbar {
  //     width: 4px;
  //     height: 0px;
  //   }
  //   &::-webkit-scrollbar-thumb {
  //     background-color: $soft-gray;
  //     box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  //     border-radius: 6px;
  //   }

  //   &::-webkit-scrollbar-track {
  //     margin-top: 48px;
  //   }

  p {
    margin: 0;
    padding: 8px 16px;
    width: 100%;
    font-size: 13px;
    &:hover {
      background-color: $soft-gray;
      cursor: pointer;
    }
  }

  h3 {
    position: sticky;
    top: 0;
    background-color: white;
    font-family: $base-font-family;
    font-weight: 100;
    padding: 16px;
    width: 100%;
    z-index: 3;
  }
}

.relative {
  position: relative;
}
</style>