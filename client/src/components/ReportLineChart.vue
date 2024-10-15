<template>
  <div>
    <line-chart :chart-data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'

export default {
  name: 'ReportLineChart',
  components: {
    LineChart: {
      extends: Line,
      props: ['chartData', 'options'],
      mounted() {
        // const ctx = this.$refs.canvas.getContext('2d')

        // const gradient1 = ctx.createLinearGradient(0, 0, 0, 400)
        // gradient1.addColorStop(0, 'rgba(138, 122, 175, 1)')
        // gradient1.addColorStop(1, 'rgba(138, 122, 175, 0.3)')
        // this.chartData.datasets[0].backgroundColor = gradient1

        // const gradient2 = ctx.createLinearGradient(0, 0, 0, 400)
        // gradient2.addColorStop(0, 'rgba(255, 99, 132, 1)')
        // gradient2.addColorStop(1, 'rgba(255, 99, 132, 0.3)')
        // this.chartData.datasets[1].backgroundColor = gradient2

        this.renderChart(this.chartData, this.options)
      },
    },
  },
  props: {
    volume: {
      default: null,
    },
    reach: {
      default: null,
    },
    dates: {
      default: null,
    },
  },
  data() {
    return {
      chartData: {
        labels: this.dates,
        datasets: [
          {
            label: 'Volume',
            data: this.volume,
            borderColor: '#FF6384',
            pointBackgroundColor: '#fff',
            pointBorderColor: '#FF6384',
            pointHoverBackgroundColor: '#FF6384',
            pointHoverBorderColor: '#fff',
            pointRadius: 5,
            pointHoverRadius: 7,
            // fill: true,
            fill: false,
            lineTension: 0.3,
          },
          {
            label: 'Reach',
            data: this.reach,
            borderColor: '#c2c4ca',
            pointBackgroundColor: '#fff',
            pointBorderColor: '#c2c4ca',
            pointHoverBackgroundColor: '#c2c4ca',
            pointHoverBorderColor: '#fff',
            pointRadius: 5,
            pointHoverRadius: 7,
            // fill: true,
            fill: false,
            lineTension: 0.3,
            yAxisID: 'y-axis-2',
          },
        ],
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 1000,
          easing: 'easeInOutQuad',
        },
        legend: {
          display: true,
          labels: {
            fontColor: '#333',
            fontSize: 14,
            padding: 16,
          },
        },
        tooltips: {
          enabled: true,
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0,0,0,0.7)',
          titleFontSize: 14,
          bodyFontSize: 12,
          footerFontSize: 12,
          xPadding: 10,
          yPadding: 10,
          caretSize: 8,
          cornerRadius: 6,
        },
        scales: {
          xAxes: [
            {
              gridLines: {
                display: false,
              },
              ticks: {
                fontColor: '#555',
                fontSize: 12,
                padding: 10,
              },
            },
          ],
          yAxes: [
            {
              id: 'y-axis-1',
              type: 'linear',
              position: 'left',
              gridLines: {
                color: 'rgba(200, 200, 200, 0.2)',
              },
              ticks: {
                beginAtZero: true,
                fontColor: '#555',
                fontSize: 12,
                padding: 10,
              },
            },
            {
              id: 'y-axis-2',
              type: 'linear',
              position: 'right',
              gridLines: {
                display: false,
              },
              ticks: {
                beginAtZero: true,
                fontColor: '#555',
                fontSize: 12,
                padding: 10,
                callback: function (value) {
                  if (value >= 1000000000) {
                    return (value / 1000000000).toFixed(1) + 'B'
                  } else if (value >= 1000000) {
                    return (value / 1000000).toFixed(1) + 'M'
                  } else if (value >= 1000) {
                    return (value / 1000).toFixed(1) + 'K'
                  } else {
                    return value
                  }
                },
              },
            },
          ],
        },
      },
    }
  },
}
</script>

<style scoped>
div {
  position: relative;
  max-width: 100%;
  margin: auto;
  height: 320px;
}
</style>
