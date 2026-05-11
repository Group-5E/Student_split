import { ChartLineInteractive } from '@/components/graph'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/statistics')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div className='h-full w-full p-5'>
      <ChartLineInteractive>

      </ChartLineInteractive>
    </div>
  )
}
