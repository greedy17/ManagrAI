<template>
  <div>
    <p>{{ taskStatus }}</p>
  </div>
</template>

<script>
export default {
  name: 'SseComponent',

  data() {
    return {
      taskStatus: null,
    }
  },
  sse: {
    cleanup: true,
  },
  mounted() {
    this.$sse
      .create('/events/')
      .on('message', (msg) => console.info('Message:', msg))
      .on('error', (err) => console.error('Failed to parse or lost connection:', err))
      .connect()
      .catch((err) => console.error('Failed to make initial connection:', err))
  },
}
</script>
